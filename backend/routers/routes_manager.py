from fastapi import APIRouter
from .auth import authrouter

apirouter = APIRouter()
apirouter.include_router(authrouter, prefix="/auth", tags=['Auth'])