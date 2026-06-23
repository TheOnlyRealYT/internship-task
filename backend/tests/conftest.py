import pytest
import pytest_asyncio
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from os import getenv


TEST_DATABASE_URL = getenv("TEST_DATABASE_URL", "")

@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as s:
        yield s

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)  # clean slate after each test
    await engine.dispose()


@pytest_asyncio.fixture
async def test_org(session):
    from backend.models.organization import Organization
    org = Organization(name="Test Org")
    session.add(org)
    await session.commit()
    await session.refresh(org)
    return org