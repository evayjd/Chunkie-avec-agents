from fastapi import FastAPI
from backend.core.config import settings
from backend.core.logging import logger
from backend.api import upload, ask, documents, retrieve
from backend.core.database import init_db
from backend.api import agent
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.include_router(upload.router)
app.include_router(ask.router)
app.include_router(documents.router)
app.include_router(retrieve.router)
app.include_router(agent.router)


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