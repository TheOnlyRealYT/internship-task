from sqlmodel import SQLModel, UniqueConstraint, Field, DateTime, Column
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import ClassVar

class RelationshipType(str, Enum):
    parent_of = "parent_of"        # domain -> subdomain
    resolves_to = "resolves_to"    # subdomain <-> ip_address
    runs_on = "runs_on"            # service -> ip_address
    covers = "covers"              # certificate -> domain/subdomain
    detected_on = "detected_on"    # technology -> subdomain/service

class AssetRelationship(SQLModel, table=True):
    __tablename__: ClassVar[str] = "asset_relationships" #type: ignore
    __table_args__ = (
        UniqueConstraint("from_asset_id", "to_asset_id", "relationship_type", name="uq_relationship"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    from_asset_id: UUID = Field(foreign_key="assets.id", index=True, ondelete="CASCADE")
    to_asset_id: UUID = Field(foreign_key="assets.id", index=True, ondelete="CASCADE")
    relationship_type: RelationshipType
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False), 
        default_factory=lambda: datetime.now(timezone.utc)
    )