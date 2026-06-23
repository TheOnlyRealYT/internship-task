import pytest
from backend.services.dedup import upsert_asset, find_existing_asset, AsyncSession
from backend.models.asset import AssetStatus
from backend.models.organization import Organization

async def test_creates_new_asset(session: AsyncSession, test_org: Organization):
    record = {"asset_type": "domain", "value": "example.com", "source": "import", "tags": [], "metadata": {}}
    asset, was_created = await upsert_asset(session, record, test_org.id)
    await session.commit()

    assert was_created is True
    assert asset.value == "example.com"

async def test_reimporting_same_asset_does_not_duplicate(session: AsyncSession, test_org: Organization):
    record = {"asset_type": "domain", "value": "example.com", "source": "import", "tags": [], "metadata": {}}

    await upsert_asset(session, record, test_org.id)
    await session.commit()

    asset2, was_created2 = await upsert_asset(session, record, test_org.id)
    await session.commit()

    assert was_created2 is False  # second import should find the existing one, not create a new row

async def test_merge_unions_tags(session: AsyncSession, test_org: Organization):
    first = {"asset_type": "domain", "value": "example.com", "tags": ["scope"], "metadata": {}}
    second = {"asset_type": "domain", "value": "example.com", "tags": ["critical"], "metadata": {}}

    await upsert_asset(session, first, test_org.id)
    await session.commit()

    asset, _ = await upsert_asset(session, second, test_org.id)
    await session.commit()

    assert set(asset.tags) == {"scope", "critical"}  # union, not overwrite

async def test_merge_advances_last_seen(session: AsyncSession, test_org: Organization):
    record = {"asset_type": "domain", "value": "example.com", "tags": [], "metadata": {}}
    asset1, _ = await upsert_asset(session, record, test_org.id)
    await session.commit()
    first_seen_time = asset1.last_seen

    asset2, _ = await upsert_asset(session, record, test_org.id)
    await session.commit()

    assert asset2.last_seen > first_seen_time

async def test_stale_asset_reactivates_on_resight(session: AsyncSession, test_org: Organization):
    record = {"asset_type": "domain", "value": "example.com", "tags": [], "metadata": {}}
    asset, _ = await upsert_asset(session, record, test_org.id)
    asset.status = AssetStatus.stale
    await session.commit()

    reimported, was_created = await upsert_asset(session, record, test_org.id)
    await session.commit()

    assert was_created is False
    assert reimported.status == AssetStatus.active