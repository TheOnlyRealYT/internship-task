from fastapi import APIRouter, Depends, HTTPException, status, responses, Query
from ..auth.security import require_role, get_current_user, hash_password, UUID
from ..models.user import User, UserRole
from ..schemas.user import GetUserResponseModel, CreateUserModel, CreateUserModelRestricted, UserChangeUsernameModel, AdminOrganizationUpdateModel, AdminUserUpdateModel
from ..services.dependencies import get_session, AsyncSession, user_already_exists_error
from ..services.utilities import get_user_by_id_or_username, get_404_error
from sqlmodel import select, func

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
    conflict_flag = await session.exec(select(User).where(User.username == user.username))
    if not conflict_flag.first() is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    result = await session.exec(select(User).where(User.username == current_user.username))
    result = result.first()
    if result is None:
        raise get_404_error("User")
    result.username = user.username
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
    user = get_user_by_id_or_username(session, username, user_id)
    await session.delete(user)
    await session.commit()
    return user

@userrouter.patch('/update-organization', dependencies=[Depends(require_role(UserRole.admin))])
async def admin_update_organization(org: AdminOrganizationUpdateModel, username: str | None = None, user_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    #org = await session.get(Organization, org.new_org_id)
    #if org.first() is None : raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization Not Found")
    #Organization Currently Not Implemeneted
    user = await get_user_by_id_or_username(session, username, user_id)
    user.org_id = org.new_org_id
    session.add(user)
    await session.commit()
    return user
    
@userrouter.put('/update-user', dependencies=[Depends(require_role(UserRole.admin))])
async def update_user_admin(new_user: AdminUserUpdateModel, username: str | None = None, user_id: UUID | None = None, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_id_or_username(session, username, user_id)
    new_user_fields = new_user.model_dump(exclude_unset=True)
    for attribute, value in new_user_fields.items():
        if attribute == "password":
            attribute = "hashed_password"
            value = hash_password(value)
        setattr(user, attribute, value)
    session.add(user)
    await session.commit()
    return user

@userrouter.get('/user-bulk-reader', dependencies=[Depends(require_role(UserRole.admin))])
async def read_many_users(
    limit: int = Query(10, ge=0, le=100),
    skip: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
    ):
    """pagenation using limit and offset, returned as well for clear reading"""
    count_statement = select(func.count()).select_from(User)
    total = (await session.exec(count_statement)).one()

    statement = select(User).offset(skip).limit(limit)
    users = (await session.exec(statement)).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": users,
    }