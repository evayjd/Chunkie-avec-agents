from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.services.roast.roast_pipeline import run_roast_pipeline


router = APIRouter(prefix="/roast", tags=["roast"])


class RoastRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    top_k: int = 6


@router.post("")
def roast_user(
    request: RoastRequest,
    db: Session = Depends(get_db),
):
    """
    Generate roast analysis from user documents
    """

    try:
        result = run_roast_pipeline(
            query=request.query,
            db=db,
            document_ids=request.document_ids,
            top_k=request.top_k,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))