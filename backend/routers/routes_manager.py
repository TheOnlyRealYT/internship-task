from fastapi import APIRouter
from .auth import authrouter
from .user import userrouter

apirouter = APIRouter()
apirouter.include_router(authrouter, prefix="/auth", tags=['Auth'])
apirouter.include_router(userrouter, prefix="/user", tags=['User'])