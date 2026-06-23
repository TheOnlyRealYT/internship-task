from fastapi import APIRouter, Depends, HTTPException, status
from backend.services.dependencies import get_session, AsyncSession
from backend.config.settings import DATABASE_URL
from sqlmodel import select
from datetime import datetime, timezone


healthrouter = APIRouter()

@healthrouter.get("/")
async def health_check(session: AsyncSession = Depends(get_session)):
    try:
        await session.exec(select(1))
        return {"status": "ok"}
    except Exception:
        print(DATABASE_URL)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database unreachable")
    
@healthrouter.get("/ping")
async def ping():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }