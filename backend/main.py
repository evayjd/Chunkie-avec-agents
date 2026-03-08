from fastapi import FastAPI
from backend.core.config import settings
from backend.core.logging import logger
from backend.api import upload, ask, documents
from backend.core.database import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    init_db()
    yield
    # shutdown (optional)


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.include_router(upload.router)
app.include_router(ask.router)
app.include_router(documents.router)


@app.get("/health")
def health_check():
    logger.info("Health check called.")
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }


@app.get("/")
def root():
    return {"message": "RAG API is running"}