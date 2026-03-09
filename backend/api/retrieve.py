from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.request_models import AskRequest
from backend.services.retrieval.retriever_factory import get_retriever
from backend.core.retrieval_config import RETRIEVAL_METHOD


router = APIRouter()


@router.post("/retrieve")
def retrieve_chunks(
    req: AskRequest,
    db: Session = Depends(get_db)
):

    retriever = get_retriever(RETRIEVAL_METHOD, db)

    chunks = retriever.retrieve(
        question=req.question,
        document_ids=req.document_ids,
        top_k=req.top_k
    )

    citations = []

    for c in chunks:

        citations.append({
            "citation_id": c["citation_id"],
            "doc_id": c["doc_id"],
            "chunk_id": c["chunk_id"],
            "chunk_index": c["chunk_index"],
            "page_start": c["page_start"],
            "page_end": c["page_end"],
            "section": c["section"],
            "snippet": c["content"][:200]
        })

    return {
        "citations": citations
    }