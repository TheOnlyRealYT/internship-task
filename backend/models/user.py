from sqlmodel import SQLModel, Field
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime


class UserRole(str, Enum):
    admin = "admin"      # full access, manage users
    analyst = "analyst"  # read/write assets
    viewer = "viewer"    # read-only

class User(SQLModel, table=True):
    __tablename__ = 'users' #type: ignore
    #known issue with SQLModel

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str = Field(exclude=True)
    role: UserRole = Field(default=UserRole.viewer)
    org_id: UUID | None = Field(default=None, foreign_key="orgs.id") # links user with an organization
    created_at: datetime = Field(default_factory=datetime.utcnow) # deprecated but used for factory