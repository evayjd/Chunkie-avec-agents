from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.request_models import AskRequest
from backend.schemas.response_models import AskResponse

from backend.services.retrieval.retriever import Retriever
from backend.services.generation.answer_generator import AnswerGenerator


router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_question(
    req: AskRequest,
    db: Session = Depends(get_db)
):

    retriever = Retriever(db)

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
            "doc_id": c["doc_id"],
            "chunk_id": c["chunk_id"],
            "chunk_index": c["chunk_index"],
            "page_start": c["page_start"],
            "page_end": c["page_end"],
            "section": c["section"],
            "snippet": c["content"][:200]
        })

    return AskResponse(
        answer=answer,
        citations=citations
    )