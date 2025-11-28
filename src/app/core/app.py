from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import load_models
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
