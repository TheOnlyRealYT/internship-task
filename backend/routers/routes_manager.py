from fastapi import APIRouter
from .auth import authrouter
from .user import userrouter
from .organization import orgrouter

apirouter = APIRouter()
apirouter.include_router(authrouter, prefix="/auth", tags=['Auth'])
apirouter.include_router(userrouter, prefix="/user", tags=['User'])
apirouter.include_router(orgrouter, prefix="/organization", tags=['Organization'])