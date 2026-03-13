"""PersonaKB FastAPI application entry point."""
 
import contextlib
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.api.routes import documents, chat, roast, health

logger = structlog.get_logger(__name__)


@contextlib.asynccontextmanager
async def lifespan(application: FastAPI):
    configure_logging()
    s = get_settings()
    logger.info("startup", app=s.app_name, env=s.app_env)
    await init_db()
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    s = get_settings()
    application = FastAPI(
        title=s.app_name,
        description="RAG ",
        version="0.1.0",
        docs_url=f"{s.api_prefix}/docs",
        redoc_url=f"{s.api_prefix}/redoc",
        openapi_url=f"{s.api_prefix}/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(s.frontend_origin)],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    prefix = s.api_prefix
    application.include_router(health.router, prefix=prefix)
    application.include_router(documents.router, prefix=prefix)
    application.include_router(chat.router, prefix=prefix)
    application.include_router(roast.router, prefix=prefix)

    return application


app = create_app()
