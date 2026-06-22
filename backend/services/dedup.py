from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models.asset import Asset, AssetStatus, AssetType
from ..models.asset_relationship import AssetRelationship, RelationshipType
from .lifecycle import touch_asset
from datetime import datetime, timezone
from uuid import UUID


async def find_existing_asset(
    session: AsyncSession,
    asset_type: AssetType,
    value: str,
    org_id,
) -> Asset | None:
    """Dedup key: (type, value, org_id) two assets are the same if all three match."""
    statement = select(Asset).where(
        Asset.asset_type == asset_type,
        Asset.value == value,
        Asset.org_id == org_id,
    )
    result = await session.exec(statement)
    return result.first()


def merge_asset(existing: Asset, incoming: dict, session: AsyncSession) -> Asset:
    """Merge an incoming record into an already-existing asset.
    Strategy: new metadata keys win on conflict, tags are unioned, last_seen always advances,
    stale assets reactivate on re-sight."""
    touch_asset(existing, session)

    incoming_tags = incoming.get("tags", [])
    existing.tags = list(set(existing.tags) | set(incoming_tags))

    incoming_metadata = incoming.get("metadata", {})
    existing.asset_metadata = {**existing.asset_metadata, **incoming_metadata}

    return existing


def create_asset_from_record(record: dict, org_id) -> Asset:
    """Build a brand new Asset from a raw incoming record."""
    return Asset(
        asset_type=record["asset_type"],
        value=record["value"],
        status=record.get("status", AssetStatus.active),
        source=record.get("source", "import"),
        tags=record.get("tags", []),
        asset_metadata=record.get("metadata", {}),
        org_id=org_id,
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
    )


def validate_record_enums(record: dict) -> dict:
    try:
        record["asset_type"] = AssetType(record["asset_type"])
    except (KeyError, ValueError):
        raise ValueError(f"Invalid or missing asset_type: '{record.get('asset_type')}'")

    if "status" in record:
        try:
            record["status"] = AssetStatus(record["status"])
        except ValueError:
            raise ValueError(f"Invalid status: '{record['status']}'")

    return record


async def upsert_asset(
    session: AsyncSession,
    record: dict,
    org_id,
) -> tuple[Asset, bool]:
    """Find-or-create a single asset record. Returns (asset, was_created)."""
    record = validate_record_enums(record)
    existing = await find_existing_asset(session, record["asset_type"], record["value"], org_id)

    if existing:
        merged = merge_asset(existing, record, session)
        touch_asset(merged, session)
        session.add(merged)
        return merged, False

    new_asset = create_asset_from_record(record, org_id)
    session.add(new_asset)
    return new_asset, True


async def create_relationship_if_missing(
    session: AsyncSession,
    from_asset_id: UUID,
    to_asset_id: UUID,
    relationship_type: RelationshipType,
) -> AssetRelationship | None:
    """Idempotent relationship creation — the relationship-level equivalent of upsert_asset's dedup."""
    statement = select(AssetRelationship).where(
        AssetRelationship.from_asset_id == from_asset_id,
        AssetRelationship.to_asset_id == to_asset_id,
        AssetRelationship.relationship_type == relationship_type,
    )
    result = await session.exec(statement)
    existing = result.first()
    if existing:
        return None  # already exists, nothing to do

    new_relationship = AssetRelationship(
        from_asset_id=from_asset_id,
        to_asset_id=to_asset_id,
        relationship_type=relationship_type,
    )
    session.add(new_relationship)
    return new_relationship


async def process_relationships(
    session: AsyncSession,
    record: dict,
    current_asset_id: UUID,
    org_id,
) -> list[str]:
    """Create any relationships implied by a 'relationships' field on the incoming record
    Targets are resolved by (type, value) within the same org, matching the asset dedup key
    Expected shape:
        "relationships": [
            {"type": "parent_of", "target": {"asset_type": "domain", "value": "example.com"}}
        ]
    Returns a list of human-readable errors for targets that couldn't be resolved, so the caller can report partial failures without crashing the batch

    This functio runs on the assumption that bulk import will only import a single organization's data at once
    """
    errors: list[str] = []

    for rel in record.get("relationships", []):
        try:
            target = rel["target"]
            target_asset = await find_existing_asset(
                session, target["asset_type"], target["value"], org_id
            )
            if target_asset is None:
                errors.append(
                    f"Relationship target not found: {target['asset_type']}:{target['value']}"
                )
                continue
            touch_asset(target_asset, session)
            await create_relationship_if_missing(
                session,
                from_asset_id=current_asset_id,
                to_asset_id=target_asset.id,
                relationship_type=RelationshipType(rel["type"]),
            )
        except Exception as e:
            errors.append(f"Malformed relationship entry {rel}: {e}")

    return errors