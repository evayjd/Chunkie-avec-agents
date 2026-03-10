from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api import agent, ask, documents, retrieve, roast, upload
from backend.core.config import settings
from backend.core.database import init_db
from backend.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期：
    - 启动时初始化数据库表
    - 关闭时目前无需额外清理
    """
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

# 注册所有 API 路由
app.include_router(upload.router)
app.include_router(ask.router)
app.include_router(documents.router)
app.include_router(retrieve.router)
app.include_router(agent.router)
app.include_router(roast.router)


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