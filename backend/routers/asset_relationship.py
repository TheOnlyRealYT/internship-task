from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from backend.services.dependencies import get_session
from backend.services.utilities import get_404_error
from backend.models.asset_relationship import AssetRelationship, RelationshipType
from backend.models.asset import Asset
from backend.schemas.asset_relationship import CreateRelationshipModel
from backend.auth.security import require_role, get_current_user
from backend.models.user import User, UserRole


relationshiprouter = APIRouter()

@relationshiprouter.post("/", dependencies=[Depends(require_role(UserRole.admin, UserRole.analyst))])
async def create_relationship(
    relationship: CreateRelationshipModel,
    session: AsyncSession = Depends(get_session),
):
    from_asset = await session.get(Asset, relationship.from_asset_id)
    to_asset = await session.get(Asset, relationship.to_asset_id)

    if from_asset is None or to_asset is None : raise get_404_error("Asset")

    new_relationship = AssetRelationship(
        from_asset_id=relationship.from_asset_id,
        to_asset_id=relationship.to_asset_id,
        relationship_type=relationship.relationship_type,
    )
    session.add(new_relationship)
    await session.commit()
    return new_relationship

@relationshiprouter.get("/{relationship_id}")
async def get_relationship(relationship_id: UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    relationship = await session.get(AssetRelationship, relationship_id)
    if relationship is None : raise get_404_error("Relationship")
    
    if user.is_elevated_user:
        return relationship
    
    from_asset = await session.get(Asset, relationship.from_asset_id)
    to_asset = await session.get(Asset, relationship.to_asset_id)

    if from_asset is None or to_asset is None : raise get_404_error("FROM asset")

    if from_asset.org_id != user.org_id or to_asset.org_id != user.org_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Can't Access Other Organization's Assets")
    return relationship

@relationshiprouter.delete("/{relationship_id}", dependencies=[Depends(require_role(UserRole.admin, UserRole.analyst))])
async def delete_relationship(relationship_id: UUID, session: AsyncSession = Depends(get_session)):
    relationship = await session.get(AssetRelationship, relationship_id)
    if relationship is None : raise get_404_error("Relationship")
    await session.delete(relationship)
    await session.commit()
    return relationship

@relationshiprouter.patch("/{relationship_id}")
async def update_relation_relationship(relationship_type: RelationshipType, relationship_id: UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    relationship = await session.get(AssetRelationship, relationship_id)
    if relationship is None : raise get_404_error("Relationship")
    
    if user.is_elevated_user:
        return relationship
    
    from_asset = await session.get(Asset, relationship.from_asset_id)
    to_asset = await session.get(Asset, relationship.to_asset_id)

    if from_asset is None or to_asset is None : raise get_404_error("FROM asset")

    if from_asset.org_id != user.org_id or to_asset.org_id != user.org_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Can't Access Other Organization's Assets")
    
    relationship.relationship_type = relationship_type
    session.add(relationship)
    await session.commit()

    return relationship