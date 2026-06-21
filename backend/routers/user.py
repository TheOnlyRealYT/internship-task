from fastapi import APIRouter, Depends
from ..auth.security import get_current_user, hash_password
from ..models.user import User
from ..schemas.user import GetUserResponseModel, CreateUserModel
from ..services.dependencies import get_session, AsyncSession, user_already_exists_error
from sqlmodel import select

userrouter = APIRouter()

@userrouter.get("/me", response_model=GetUserResponseModel)
async def get_current_user_profile(user: User = Depends(get_current_user)):
    return user

@userrouter.post('/create-user', response_model=GetUserResponseModel)
async def create_new_user(user: CreateUserModel, session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(User).where(User.username == user.username))
    if result.first():
        raise user_already_exists_error
    dbuser = User(username = user.username, org_id=user.org_id, role = user.role, hashed_password=hash_password(user.password))
    session.add(dbuser)
    await session.commit()
    return dbuser