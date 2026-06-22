from fastapi import APIRouter, Depends
from ..services.dedup import upsert_asset, process_relationships
from ..services.dependencies import get_session
from ..auth.security import require_role
from ..models.user import UserRole
from ..models.asset import Asset, AssetSource
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()

@router.post("/ingest", dependencies=[Depends(require_role(UserRole.admin, UserRole.analyst))])
async def ingest_assets(records: list[dict], org_id: UUID, session: AsyncSession = Depends(get_session)):
    created, updated, failed = [], [], []
    processed: list[tuple[dict, Asset]] = []

    for record in records:
        try:
            async with session.begin_nested():
                record['source'] = AssetSource.import_
                asset, was_created = await upsert_asset(session, record, org_id)
                await session.flush()
                (created if was_created else updated).append(asset.id)
                processed.append((record, asset))
        except Exception as e:
            failed.append({"record": record, "error": str(e)})

    for record, asset in processed:
        try:
            async with session.begin_nested():
                rel_errors = await process_relationships(session, record, asset.id, org_id)
                await session.flush()
                for err in rel_errors:
                    failed.append({"record": record, "error": err})
        except Exception as e:
            failed.append({"record": record, "error": str(e)})

    await session.commit()

    return {"created": created, "updated": updated, "failed": failed}