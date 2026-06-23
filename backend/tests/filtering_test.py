from sqlmodel import select
from backend.models.asset import Asset, AssetType, AssetStatus, AssetSource, UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import col, any_

async def _make_assets(session: AsyncSession, org_id: UUID):
    assets = [
        Asset(asset_type=AssetType.domain, value="a.com", status=AssetStatus.active, source=AssetSource.import_, tags=["prod"], org_id=org_id),
        Asset(asset_type=AssetType.subdomain, value="api.a.com", status=AssetStatus.stale, source=AssetSource.import_, tags=["api"], org_id=org_id),
        Asset(asset_type=AssetType.domain, value="b.com", status=AssetStatus.active, source=AssetSource.import_, tags=["staging"], org_id=org_id),
    ]
    session.add_all(assets)
    await session.commit()
    return assets

async def test_filter_by_type(session: AsyncSession, test_org):
    await _make_assets(session, test_org.id)
    result = await session.exec(select(Asset).where(Asset.asset_type == AssetType.domain))
    domains = result.all()
    assert len(domains) == 2

async def test_filter_by_status(session: AsyncSession, test_org):
    await _make_assets(session, test_org.id)
    result = await session.exec(select(Asset).where(Asset.status == AssetStatus.stale))
    stale = result.all()
    assert len(stale) == 1
    assert stale[0].value == "api.a.com"

async def test_filter_by_tag(session: AsyncSession, test_org):
    await _make_assets(session, test_org.id)
    result = await session.exec(select(Asset).where("prod" == any_(Asset.tags)))
    tagged = result.all()
    assert len(tagged) == 1

async def test_value_contains_filter(session: AsyncSession, test_org):
    await _make_assets(session, test_org.id)
    result = await session.exec(select(Asset).where(col(Asset.value).ilike("%api%")))
    matches = result.all()
    assert len(matches) == 1

async def test_pagination_limits_results(session: AsyncSession, test_org):
    await _make_assets(session, test_org.id)
    result = await session.exec(select(Asset).limit(2))
    assert len(result.all()) == 2