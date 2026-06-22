from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime


class Organization(SQLModel, table=True):
    __tablename__ = "orgs" # type: ignore
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow) # deprecated but used for factory
