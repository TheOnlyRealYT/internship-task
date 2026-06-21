from fastapi import APIRouter, Depends, HTTPException, status
from ..services.dependencies import get_session, credentials_exception
from ..auth.security import Authenticate_user, create_access_token, Token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from ..models.user import User

authrouter = APIRouter()

@authrouter.post('/token')
async def login(username: str, password: str, session: AsyncSession = Depends(get_session)):
    statement = select(User).where(User.username == username)
    result = await session.execute(statement)
    user = result.first()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User Not Registered")
    user = User(**dict(user))
    
    authenticated_user = await Authenticate_user(user, password)
    if not authenticated_user:
        raise credentials_exception
    
    access_token = create_access_token(data={"sub": str(authenticated_user.id)})
    return Token(access_token=access_token, token_type="bearer")