from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..auth.security import require_role, get_current_user
from ..services.dependencies import get_session, cant_access_other_org_error
from ..services.utilities import get_404_error
from ..services.lifecycle import touch_asset
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, any_, update, col, or_
from ..models.user import User, UserRole
from ..models.asset_relationship import AssetRelationship
from ..models.asset import Asset, AssetType, AssetStatus, AssetSource
from uuid import UUID
from ..schemas.asset import CreateAssetModel, UpdateAssetModel
from datetime import datetime, timezone, timedelta

assetrouter = APIRouter()

@assetrouter.get("/summary")
async def get_asset_summary(
    org_id: UUID | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    aggregation data for dashboards
    """
    type_statement = select(Asset.asset_type, func.count()).group_by(Asset.asset_type)
    status_statement = select(Asset.status, func.count()).group_by(Asset.status)

    if current_user.is_elevated_user:
        if org_id:
            type_statement = type_statement.where(Asset.org_id == org_id)
            status_statement = status_statement.where(Asset.org_id == org_id)
    else:
        if org_id != current_user.org_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Can't Access Summary Of Another Organization")
        type_statement = type_statement.where(Asset.org_id == current_user.org_id)
        status_statement = status_statement.where(Asset.org_id == current_user.org_id)

    type_results = (await session.exec(type_statement)).all()
    status_results = (await session.exec(status_statement)).all()

    by_type = {
        (t if hasattr(t, "value") else t): count 
        for t, count in type_results
    }
    by_status = {
        (s if hasattr(s, "value") else s): count 
        for s, count in status_results
    }

    total_count = sum(by_type.values())

    return {
        "total_count": total_count,
        "by_type": by_type,
        "by_status": by_status,
    }

@assetrouter.get("/{asset_id}")
async def get_asset(asset_id: UUID, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    asset = await session.get(Asset, asset_id)
    if asset is None : raise get_404_error("Asset")
    touch_asset(asset, session)
    if asset.org_id == current_user.org_id or current_user.is_elevated_user:
        await session.commit()
        return asset
    raise cant_access_other_org_error

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
        if org_id and org_id != current_user.org_id:
            raise cant_access_other_org_error
        statement = statement.where(Asset.org_id == current_user.org_id)

    if type:
        statement = statement.where(Asset.asset_type == type)
    if status_:
        statement = statement.where(Asset.status == status_)
    if tag:
        statement = statement.where(tag == any_(Asset.tags))

    sort_column = getattr(Asset, sort_by, None)
    if sort_column is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid sort_by field: {sort_by}")
    statement = statement.order_by(sort_column)

    count_statement = select(func.count()).select_from(statement.subquery())
    total = (await session.exec(count_statement)).one()

    statement = statement.offset(skip).limit(limit)
    result = await session.exec(statement)
    assets = result.all()
    for asset in assets:
        touch_asset(asset, session)

    await session.commit()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": assets,
    }

@assetrouter.post("/", dependencies=[Depends(require_role(UserRole.admin, UserRole.analyst))])
async def create_asset(new_asset: CreateAssetModel, session: AsyncSession = Depends(get_session)):
    asset = Asset(**new_asset.model_dump())
    session.add(asset)
    await session.commit()
    return asset

@assetrouter.delete("/{asset_id}", dependencies=[Depends(require_role(UserRole.admin, UserRole.analyst))])
async def delete_asset(asset_id: UUID, session: AsyncSession = Depends(get_session)):
    asset = await session.get(Asset, asset_id)
    await session.delete(asset)
    await session.commit()
    return asset

@assetrouter.put("/{asset_id}", dependencies=[Depends(require_role(UserRole.admin, UserRole.analyst))])
async def update_asset(asset_id: UUID, new_asset: UpdateAssetModel, session: AsyncSession = Depends(get_session)):
    asset = await session.get(Asset, asset_id)
    if asset is None : raise get_404_error("Asset")
    touch_asset(asset, session)
    for attribute, value in new_asset.model_dump(exclude_unset=True).items():
        setattr(asset, attribute, value)
    session.add(asset)
    await session.commit()
    return asset

@assetrouter.patch("/{asset_id}", dependencies=[Depends(require_role(UserRole.admin, UserRole.analyst))])
async def add_tags(asset_id: UUID, new_tags: list[str], session: AsyncSession = Depends(get_session)):
    asset = await session.get(Asset, asset_id)
    if asset is None : raise get_404_error("Asset")
    touch_asset(asset, session)
    asset.tags += new_tags
    session.add(asset)
    await session.commit()
    return asset

@assetrouter.post('/admin/lifecycle-reap', dependencies=[Depends(require_role(UserRole.admin))])
async def bulk_lifecycle_update(session: AsyncSession = Depends(get_session)):
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=7)
    archive_cutoff = now - timedelta(days=30)

    stale_result = await session.exec(
        update(Asset)
        .where(col(Asset.status) == AssetStatus.active)
        .where(col(Asset.last_seen) < stale_cutoff)
        .values(status=AssetStatus.stale)
        )

    archive_result = await session.exec(
        update(Asset)
        .where(col(Asset.status) == AssetStatus.stale)
        .where(col(Asset.last_seen) < archive_cutoff)
        .values(status=AssetStatus.archived)
        )

    await session.commit()

    return {
        "message": "Asset lifecycle sweeping complete.",
        "marked_stale": stale_result.rowcount,
        "marked_archived": archive_result.rowcount,
    }

@assetrouter.get("/{asset_id}/graph")
async def get_asset_graph(asset_id: UUID, current_user: User = Depends(get_current_user),  session: AsyncSession = Depends(get_session)):
    asset = await session.get(Asset, asset_id)
        
    if asset is None:
        raise get_404_error("Asset")
    
    if not current_user.is_elevated_user:
        if asset.org_id != current_user.org_id:
            raise cant_access_other_org_error

    statement = select(AssetRelationship).where(
        or_(
            AssetRelationship.from_asset_id == asset_id,
            AssetRelationship.to_asset_id == asset_id,
        )
    )
    result = await session.exec(statement)
    relationships = result.all()

    related_ids = set()
    for rel in relationships:
        related_ids.add(rel.from_asset_id)
        related_ids.add(rel.to_asset_id)
    related_ids.discard(asset_id) 

    related_assets = []
    if related_ids:
        related_statement = select(Asset).where(col(Asset.id).in_(related_ids))
        related_result = await session.exec(related_statement)
        related_assets = related_result.all()

    return {
        "asset": asset,
        "relationships": relationships,
        "related_assets": related_assets,
    }