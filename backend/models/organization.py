from sqlmodel import SQLModel, Field, Column, DateTime
from uuid import UUID, uuid4
from datetime import datetime, timezone


class Organization(SQLModel, table=True):
    __tablename__ = "orgs" # type: ignore
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False), 
        default_factory=lambda: datetime.now(timezone.utc)
    )
