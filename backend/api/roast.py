from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.request_models import RoastRequest
from backend.schemas.response_models import RoastResponse
from backend.services.roast.roast_pipeline import run_roast_pipeline

router = APIRouter(prefix="/roast", tags=["roast"])


@router.post("", response_model=RoastResponse)
def roast_user(
    request: RoastRequest,
    db: Session = Depends(get_db),
):
    """
    Roast 分析接口。
    """
    try:
        result = run_roast_pipeline(
            query=request.query,
            db=db,
            document_ids=request.document_ids,
            top_k=request.top_k,
            method=request.method,
            style_preference=request.style_preference,
        )
        return result

    except ValueError as e:
        # 输入问题走 400
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))