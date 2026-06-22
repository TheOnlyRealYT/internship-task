from datetime import datetime, timezone
from ..models.asset import Asset, AssetStatus
from sqlmodel.ext.asyncio.session import AsyncSession

def touch_asset(asset: Asset, session: AsyncSession) -> None:
    """Update last_seen and reactivate if previously stale also adds to the current session orm data"""
    asset.last_seen = datetime.now(timezone.utc)
    if asset.status == AssetStatus.stale:
        asset.status = AssetStatus.active
    session.add(asset)