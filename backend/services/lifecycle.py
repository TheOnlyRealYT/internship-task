# services/lifecycle.py
from datetime import datetime, timezone
from ..models.asset import Asset, AssetStatus

def touch_asset(asset: Asset) -> Asset:
    """Update last_seen and reactivate if previously stale."""
    asset.last_seen = datetime.now(timezone.utc)
    if asset.status == AssetStatus.stale:
        asset.status = AssetStatus.active
    return asset