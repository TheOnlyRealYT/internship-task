from fastapi import APIRouter, Depends, HTTPException, status, responses
from ..auth.security import require_role, get_current_user, hash_password, UUID
from ..models.user import User, UserRole
from ..schemas.user import GetUserResponseModel, CreateUserModel, CreateUserModelRestricted, UserChangeUsernameModel
from ..services.dependencies import get_session, AsyncSession, user_already_exists_error
from sqlmodel import select, update

userrouter = APIRouter()

@userrouter.get("/me", response_model=GetUserResponseModel)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Gets current user who is authenticated with an access token"""
    return current_user

@userrouter.post('/create-user', response_model=GetUserResponseModel, dependencies=[Depends(require_role(UserRole.admin))])
async def create_new_user(user: CreateUserModel, session: AsyncSession = Depends(get_session)):
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

@userrouter.patch('/change-username', response_model=GetUserResponseModel)
async def change_username(user: UserChangeUsernameModel, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    conflict_flag = await session.exec(select(User).where(User.username == user.new_username))
    if not conflict_flag.first() is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    result = await session.exec(select(User).where(User.username == current_user.username))
    result = result.first()
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found")
    result.username = user.new_username
    session.add(result)
    await session.commit()
    await session.refresh(result)
    return result

@userrouter.delete('/delete-me')
async def delete_current_user(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    try:
        await session.delete(current_user)
        await session.commit()
        return responses.Response({"details": "Deleted Successfully"}, status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"ERROR: {e}")
    

@userrouter.delete('/delete-user', dependencies=[Depends(require_role(UserRole.admin))])
async def admin_delete_current_user(username: str | None = None, user_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    if user_id:
        user = await session.get(User, user_id)
        if not user : raise HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found")
        await session.delete(user)
        await session.commit()
        return user
    elif username:
        user = await session.exec(select(User).where(User.username == username))
        user = user.first()
        if not user : raise HTTPException(status.HTTP_404_NOT_FOUND, "User Not Found")
        await session.delete(user)
        await session.commit()
        return user
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Include a query of either username or id")