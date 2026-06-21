from fastapi import FastAPI
from .routers.routes_manager import apirouter
from .context.context_manager import lifespan

app = FastAPI(debug=True, lifespan=lifespan)

app.include_router(apirouter, prefix='/api/v1')