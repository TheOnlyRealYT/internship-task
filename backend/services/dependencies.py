from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from os import getenv
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from fastapi import HTTPException, status


load_dotenv()
DATABASE_URL = getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise Exception("No Database URL Found")

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