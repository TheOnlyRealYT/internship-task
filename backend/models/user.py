from sqlmodel import SQLModel, Field, DateTime, Column
from pydantic import field_validator
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone


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
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False), 
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_elevated_user(self) -> bool:
        return self.role in {UserRole.admin, UserRole.analyst}