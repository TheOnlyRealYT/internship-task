from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from ..services.dependencies import get_session
from ..services.utilities import get_404_error
from ..models.organization import Organization
from ..models.user import UserRole
from ..auth.security import require_role
from uuid import UUID

orgrouter = APIRouter()

@orgrouter.get('/organization/{org_id}')
async def get_organization(org_id: UUID, session: AsyncSession = Depends(get_session)):
    return await session.get(Organization, org_id)

@orgrouter.get('/organization/')
async def get_many_orgs(
    limit: int = Query(10, ge=0, le=100),
    skip: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
    ):
    """pagenation using limit and offset, returned as well for clear reading"""
    count_statement = select(func.count()).select_from(Organization)
    total = (await session.exec(count_statement)).one()

    statement = select(Organization).offset(skip).limit(limit)
    orgs = (await session.exec(statement)).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": orgs,
    }

@orgrouter.put("/organization/{org_id}", dependencies=[Depends(require_role(UserRole.admin))])
async def update_org(org_id: UUID, name: str, session: AsyncSession = Depends(get_session)):
    org = await session.get(Organization, org_id)
    if org is None : raise get_404_error("Organization")
    org.name = name
    session.add(org)
    await session.commit()
    return org