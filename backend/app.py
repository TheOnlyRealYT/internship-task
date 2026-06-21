from fastapi import FastAPI
from .routes import apirouter
from .context_manager import lifespan

app = FastAPI(debug=True, lifespan=lifespan)