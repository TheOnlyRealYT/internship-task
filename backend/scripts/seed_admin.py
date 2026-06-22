import asyncio
from backend.services.dependencies import async_session
from backend.models.user import User, UserRole
from backend.auth.security import hash_password

async def seed_admin():
    async with async_session() as session:
        admin = User(
            username="admin",
            hashed_password=hash_password("changeme123"),  # change immediately after first login
            role=UserRole.admin,
            org_id=None,
        )
        session.add(admin)
        await session.commit()
        print(f"Admin created: {admin.username} / id={admin.id}")

if __name__ == "__main__":
    asyncio.run(seed_admin())