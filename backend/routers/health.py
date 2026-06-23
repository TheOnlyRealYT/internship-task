from fastapi import APIRouter, Depends, HTTPException, status
from backend.services.dependencies import get_session, AsyncSession
from backend.config.settings import DATABASE_URL
from sqlmodel import select


healthrouter = APIRouter()

@healthrouter.get("/")
async def health_check(session: AsyncSession = Depends(get_session)):
    try:
        await session.exec(select(1))
        return {"status": "ok"}
    except Exception:
        print(DATABASE_URL)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database unreachable")