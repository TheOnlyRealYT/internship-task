from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Literal



class AssetType(str, Enum):
    domain = "domain"
    subdomain = "subdomain"
    ip_address = "ip_address"
    service = "service"
    certificate = "certificate"
    technology = "technology"

class AssetStatus(str, Enum):
    active = "active"
    stale = "stale"
    archived = "archived"

class Asset(SQLModel, table=True):
    __tablename__ = "Assets" # type: ignore
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    asset_type: AssetType
    value: str
    first_seen: datetime = Field(default_factory=datetime.utcnow) # deprecated but used for factory
    last_seen: datetime = first_seen
    status: AssetStatus = AssetStatus.active
    source: Literal["import", "scan", "manual"] = "manual"
    tags: list[str] = []
    asset_metadata: dict = Field(default={}, sa_column=Column(JSONB))
    org_id: UUID | None = Field(default=None, foreign_key="orgs.id") # links asset with an organization