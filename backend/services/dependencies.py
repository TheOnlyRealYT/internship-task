from ..settings.config import DATABASE_URL
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from fastapi import HTTPException, status


engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    """Async Generator For Sessions, Use To Access DataBAse On Each Route"""
    async with async_session() as session:
        yield session

#common errors
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

user_already_exists_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User Already Exists"
)