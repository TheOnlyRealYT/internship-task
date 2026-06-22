from fastapi import APIRouter, Depends
from ..services.dedup import upsert_asset
from ..services.dependencies import get_session
from ..auth.security import require_role
from ..models.user import UserRole
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()

@router.post("/ingest", dependencies=[Depends(require_role(UserRole.admin, UserRole.analyst))])
async def ingest_assets(
    records: list[dict],
    org_id: UUID | None = None,
    session: AsyncSession = Depends(get_session)
):
    created, updated, failed = [], [], []

    for record in records:
        try:
            asset, was_created = await upsert_asset(session, record, org_id)
            (created if was_created else updated).append(asset.id)
        except Exception as e:
            failed.append({"record": record, "error": str(e)})

    await session.commit()
    return {"created": created, "updated": updated, "failed": failed}