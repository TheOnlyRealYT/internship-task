# services/dedup.py
from sqlmodel import select, Relationship
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models.asset import Asset, AssetStatus, AssetType, AssetTagLink, AssetTag
from .lifecycle import touch_asset
from datetime import datetime, timezone


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


def merge_asset(existing: Asset, incoming: dict) -> Asset:
    """Merge an incoming record into an already-existing asset
    Strategy: new metadata keys win on conflict, tags are unioned, last_seen always advances, stale assets reactivate on re-sight."""
    touch_asset(existing)

    incoming_tags = incoming.get("tags", [])
    existing.tags = list(set(existing.tags) | set(incoming_tags))

    incoming_metadata = incoming.get("metadata", {})
    existing.asset_metadata = {**existing.asset_metadata, **incoming_metadata}

    return existing


def create_asset_from_record(record: dict, org_id) -> Asset:
    """Build a brand new Asset from a raw incoming record."""
    return Asset(
        asset_type=record["type"],
        value=record["value"],
        status=record.get("status", AssetStatus.active),
        source=record.get("source", "import"),
        tags=record.get("tags", []),
        asset_metadata=record.get("metadata", {}),
        org_id=org_id,
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
    )


async def upsert_asset(
    session: AsyncSession,
    record: dict,
    org_id,
) -> tuple[Asset, bool]:
    """Find-or-create a single asset record. Returns (asset, was_created)."""
    existing = await find_existing_asset(session, record["type"], record["value"], org_id)

    if existing:
        merged = merge_asset(existing, record)
        session.add(merged)
        return merged, False

    new_asset = create_asset_from_record(record, org_id)
    session.add(new_asset)
    return new_asset, True