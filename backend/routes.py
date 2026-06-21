from fastapi import APIRouter, Depends
from .utilities import get_session

apirouter = APIRouter(prefix="/api/v1")
