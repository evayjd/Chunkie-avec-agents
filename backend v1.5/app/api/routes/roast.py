"""Roast / persona analysis endpoints."""
 
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.roast import RoastRequest, RoastProfileOut
from app.services.roast_service import RoastService

router = APIRouter(prefix="/roast", tags=["roast"])


@router.post("/", response_model=RoastProfileOut)
async def generate_roast(
    request: RoastRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = RoastService(db)
    try:
        return await svc.generate_roast(
            document_ids=request.document_ids,
            language=request.language or "zh",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
