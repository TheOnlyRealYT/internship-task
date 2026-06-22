from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from backend.models.user import User
from sqlmodel import select
from fastapi import HTTPException, status


def get_404_error(missing: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{missing} Not Found")

async def get_user_by_id_or_username(
    session: AsyncSession,
    username: str | None = None,
    user_id: UUID | None = None,
) -> User:
    """User Search by id or username utility"""
    if user_id:
        user = await session.get(User, user_id)
    elif username:
        result = await session.exec(select(User).where(User.username == username))
        user = result.first()
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Include a query of either username or id")

    if not user:
        raise get_404_error("User")

    return user