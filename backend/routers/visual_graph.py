from fastapi.responses import FileResponse
from fastapi import APIRouter

graphrouter = APIRouter()

@graphrouter.get("/")
async def graph_viewer():
    return FileResponse("../backend/static/graph.html")