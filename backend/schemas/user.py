from pydantic import BaseModel, Field
from datetime import datetime
from ..models.user import UserRole
from uuid import UUID

class GetUserResponseModel(BaseModel):
    """Model for getting user from a dedicated get request"""
    username: str
    org: str | UUID | None = None
    role: UserRole = Field(default=UserRole.viewer)
    created_at: datetime

class BulkReaderResponseModel(BaseModel):
    """Model for user model read by a bulk reader"""
    username: str
    org: str

class CreateUserModel(BaseModel):
    """Model for user creation to separate database model from user interactable model"""
    password: str = Field(exclude=True)
    username: str
    role: UserRole = Field(default=UserRole.viewer)
    org_id: UUID | None = None

class UserChangeUsernameModel(BaseModel):
    """Model for username change operations"""
    new_username: str

class AdminUserUpdateModel(BaseModel):
    """Model for admin updating users"""
    new_username: str | None = None
    new_password: str | None = None
    role: UserRole | None = None
    org_id: UUID | None = None