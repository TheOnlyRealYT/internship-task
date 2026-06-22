from pydantic import BaseModel, Field
from uuid import UUID

from backend.models.asset_relationship import RelationshipType

class CreateRelationshipModel(BaseModel):
    from_asset_id: UUID
    to_asset_id: UUID
    relationship_type: RelationshipType