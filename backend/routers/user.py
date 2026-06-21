from fastapi import APIRouter, Depends
from ..auth.security import get_current_user
from ..models.user import User

userrouter = APIRouter()

@userrouter.get("/me")
async def get_current_user_profile(user: User = Depends(get_current_user)):
    return user