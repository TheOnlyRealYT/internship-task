from fastapi import APIRouter
from .auth import authrouter
from .user import userrouter
from .organization import orgrouter
from .bulkimport import router
from .asset import assetrouter
from .asset_relationship import relationshiprouter

apirouter = APIRouter()
apirouter.include_router(authrouter, prefix="/auth", tags=['Auth'])
apirouter.include_router(userrouter, prefix="/users", tags=['User'])
apirouter.include_router(orgrouter, prefix="/organizations", tags=['Organization'])
apirouter.include_router(router, prefix="/import", tags=['Asset'])
apirouter.include_router(assetrouter, prefix="/assets", tags=['Asset'])
apirouter.include_router(relationshiprouter, prefix="/relationships", tags=['relationship'])