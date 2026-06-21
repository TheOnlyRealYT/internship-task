from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from os import getenv
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker


load_dotenv()
DATABASE_URL = getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise Exception("No Database URL Found")

connect_args = {"check_same_thread": False} #making sure fastapi can multithread
engine = create_async_engine(DATABASE_URL, connect_args=connect_args)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    """Async Generator For Sessions, Use To Access DataBAse On Each Route"""
    async with async_session() as session:
        yield session