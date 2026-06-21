from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4


class Organization(SQLModel, table=True):
    __tablename__ = "orgs" # type: ignore
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str