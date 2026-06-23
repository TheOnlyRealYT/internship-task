from pydantic import BaseModel, Field
from backend.models.asset import AssetStatus, AssetType
from uuid import UUID

class CreateAssetModel(BaseModel):
    asset_type: AssetType
    value: str
    org_id: UUID # links asset with an organization
    asset_metadata: dict = {}
    tags: list[str] = [] 

class UpdateAssetModel(BaseModel):
    asset_type: AssetType | None = None
    value: str | None = None
    asset_metadata: dict | None = None
    org_id: UUID | None = None # links asset with an organization
    tags: list[str] | None = None 