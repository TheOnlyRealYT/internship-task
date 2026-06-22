from contextlib import asynccontextmanager
from backend.services.dependencies import engine
from sqlmodel import SQLModel
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield
    
    await engine.dispose()