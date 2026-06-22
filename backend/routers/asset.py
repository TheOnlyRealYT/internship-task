from fastapi import APIRouter, Depends, HTTPException, status
from ..auth.security import require_role, get_current_user
from ..services.dependencies import get_session
from ..services.utilities import get_404_error
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models.user import User, UserRole
from ..models.asset import Asset
from uuid import UUID

assetrouter = APIRouter()

@assetrouter.get("/{asset_id}")
async def get_asset(asset_id: UUID, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    asset = await session.get(Asset, asset_id)
    if asset is None : raise get_404_error("Asset")
    if asset.org_id == current_user.org_id or current_user.is_elevated_user:
        return asset
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Can't Access Another Organization's Assets")
