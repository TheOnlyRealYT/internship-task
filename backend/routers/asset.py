from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..auth.security import require_role, get_current_user
from ..services.dependencies import get_session
from ..services.utilities import get_404_error
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from ..models.user import User, UserRole
from ..models.asset import Asset, AssetType, AssetStatus, AssetSource
from uuid import UUID

assetrouter = APIRouter()

@assetrouter.get("/{asset_id}")
async def get_asset(asset_id: UUID, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    asset = await session.get(Asset, asset_id)
    if asset is None : raise get_404_error("Asset")
    if asset.org_id == current_user.org_id or current_user.is_elevated_user:
        return asset
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Can't Access Another Organization's Assets")

@assetrouter.get("/")
async def get_assets(
    type: AssetType | None = Query(None),
    status_: AssetStatus | None = Query(AssetStatus.active),
    tag: str | None = Query(None),
    sort_by: str = Query("last_seen"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    org_id: UUID | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement = select(Asset)
    if current_user.is_elevated_user:
        if org_id:
            statement = statement.where(Asset.org_id == org_id)
    else:
        statement = statement.where(Asset.org_id == current_user.org_id)

    if type:
        statement = statement.where(Asset.asset_type == type)
    if status_:
        statement = statement.where(Asset.status == status_)
    if tag:
        statement = statement.where(Asset.tags.__contains__([tag]))

    sort_column = getattr(Asset, sort_by, None)
    if sort_column is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid sort_by field: {sort_by}")
    statement = statement.order_by(sort_column)

    count_statement = select(func.count()).select_from(statement.subquery())
    total = (await session.exec(count_statement)).one()

    statement = statement.offset(skip).limit(limit)
    result = await session.exec(statement)
    assets = result.all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": assets,
    }