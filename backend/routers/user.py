from fastapi import APIRouter, Depends, HTTPException, status
from ..auth.security import require_role, get_current_user, hash_password
from ..models.user import User, UserRole
from ..schemas.user import GetUserResponseModel, CreateUserModel, CreateUserModelRestricted
from ..services.dependencies import get_session, AsyncSession, user_already_exists_error
from sqlmodel import select

userrouter = APIRouter()

@userrouter.get("/me", response_model=GetUserResponseModel)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Gets current user who is authenticated with an access token"""
    return current_user

@userrouter.post('/create-user', response_model=GetUserResponseModel)
async def create_new_user(user: CreateUserModel, current_user: User = Depends(require_role(UserRole.admin)), session: AsyncSession = Depends(get_session)):
    """Creates a new user at the admin levels, can specify the user access level"""
    result = await session.exec(select(User).where(User.username == user.username))
    if result.first():
        raise user_already_exists_error
    dbuser = User(username = user.username, org_id=user.org_id, role = user.role, hashed_password=hash_password(user.password))
    session.add(dbuser)
    await session.commit()
    return dbuser

@userrouter.post('/register', response_model=GetUserResponseModel)
async def register_user(user: CreateUserModelRestricted, session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(User).where(User.username == user.username))
    if result.first():
        raise user_already_exists_error
    dbuser = User(username = user.username, org_id=user.org_id, role = UserRole.viewer, hashed_password=hash_password(user.password))
    session.add(dbuser)
    await session.commit()
    return dbuser