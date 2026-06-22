from sqlmodel import SQLModel, Field, Column, ARRAY, String
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Literal, Optional



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

class AssetSource(str, Enum):
    import_ = "import"
    scan = "scan"
    manual = "manual"

class Asset(SQLModel, table=True):
    __tablename__ = "assets" # type: ignore
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    asset_type: AssetType
    value: str
    first_seen: datetime = Field(default_factory=datetime.utcnow) # deprecated but used for factory
    last_seen: datetime = Field(default_factory=datetime.utcnow) 
    status: AssetStatus = AssetStatus.active
    source: AssetSource = AssetSource.manual
    asset_metadata: dict = Field(default={}, sa_column=Column(JSONB))
    org_id: UUID | None = Field(default=None, foreign_key="orgs.id") # links asset with an organization
    tags: list[str] = Field(default=[], sa_column=Column(ARRAY(String)))