from argon2 import PasswordHasher
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt, dotenv, os
from jwt.exceptions import InvalidTokenError
from ..models.user import User, UserRole
from ..services.dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.dependencies import credentials_exception

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: UUID | None = None

dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 0.0))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

password_context = PasswordHasher()

def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(hashed_password: str, password: str) -> bool:
    try:
        return password_context.verify(hashed_password, password)
    except:
        return False

async def Authenticate_user(user: User, password: str):
    if not verify_password(user.hashed_password, password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except InvalidTokenError:
        raise credentials_exception

    user = await session.get(User, token_data.id)

    if user is None:
        raise credentials_exception
    return user

def require_role(*allowed_roles: UserRole):
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in allowed_roles]}"
            )
        return user
    return role_checker