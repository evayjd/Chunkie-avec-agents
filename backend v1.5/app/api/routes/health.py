"""Health check endpoint."""
from fastapi import APIRouter
from app.providers.llm import get_llm_provider
from app.providers.embedding import get_embedding_provider

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "PersonaKB Backend",
    }


@router.get("/health/deep")
async def health_deep():
    llm_ok = await get_llm_provider().health_check()
    emb_ok = await get_embedding_provider().health_check()
    return {
        "status": "ok" if (llm_ok and emb_ok) else "degraded",
        "llm": llm_ok,
        "embedding": emb_ok,
    }
