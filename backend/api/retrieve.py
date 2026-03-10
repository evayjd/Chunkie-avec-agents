from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.request_models import AskRequest
from backend.services.retrieval.retriever_factory import get_retriever

router = APIRouter()


@router.post("/retrieve")
def retrieve_chunks(
    req: AskRequest,
    db: Session = Depends(get_db)
):
    """
    纯检索接口。
    """
    retriever = get_retriever(req.method, db)

    chunks = retriever.retrieve(
        question=req.question,
        document_ids=req.document_ids,
        top_k=req.top_k
    )

    citations = []

    for c in chunks:
        citations.append({
            "citation_id": c["citation_id"],
            "doc_id": c.get("doc_id"),
            "chunk_id": c.get("chunk_id"),
            "chunk_index": c.get("chunk_index"),
            "page_start": c.get("page_start"),
            "page_end": c.get("page_end"),
            "section": c.get("section"),
            "snippet": c.get("content", "")[:200]
        })

    return {
        "citations": citations
    }