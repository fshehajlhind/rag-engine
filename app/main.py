from contextlib import asynccontextmanager

from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database import engine
from app.models import Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine) # db is created on startup
    yield
app = FastAPI(title="RAG Search Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router)

