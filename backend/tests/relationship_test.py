from backend.services.dedup import upsert_asset, create_relationship_if_missing
from backend.models.asset_relationship import RelationshipType

async def test_create_relationship(session, test_org):
    domain, _ = await upsert_asset(session, {"asset_type": "domain", "value": "example.com", "tags": [], "metadata": {}}, test_org.id)
    sub, _ = await upsert_asset(session, {"asset_type": "subdomain", "value": "api.example.com", "tags": [], "metadata": {}}, test_org.id)
    await session.commit()

    rel = await create_relationship_if_missing(session, domain.id, sub.id, RelationshipType.parent_of)
    await session.commit()

    assert rel is not None
    assert rel.from_asset_id == domain.id
    assert rel.to_asset_id == sub.id

async def test_duplicate_relationship_not_created(session, test_org):
    domain, _ = await upsert_asset(session, {"asset_type": "domain", "value": "example.com", "tags": [], "metadata": {}}, test_org.id)
    sub, _ = await upsert_asset(session, {"asset_type": "subdomain", "value": "api.example.com", "tags": [], "metadata": {}}, test_org.id)
    await session.commit()

    await create_relationship_if_missing(session, domain.id, sub.id, RelationshipType.parent_of)
    await session.commit()

    second_attempt = await create_relationship_if_missing(session, domain.id, sub.id, RelationshipType.parent_of)
    await session.commit()

    assert second_attempt is None  #already exists, shouldnt create a duplicate