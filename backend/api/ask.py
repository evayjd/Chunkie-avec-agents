from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.request_models import AskRequest
from backend.schemas.response_models import AskResponse
from backend.services.generation.answer_generator import AnswerGenerator
from backend.services.retrieval.retriever_factory import get_retriever

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_question(
    req: AskRequest,
    db: Session = Depends(get_db)
):
    """
    RAG 问答接口。
    """
    retriever = get_retriever(req.method, db)

    chunks = retriever.retrieve(
        question=req.question,
        document_ids=req.document_ids,
        top_k=req.top_k
    )

    generator = AnswerGenerator()
    answer = generator.generate(req.question, chunks)

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

    return AskResponse(
        answer=answer,
        citations=citations
    )