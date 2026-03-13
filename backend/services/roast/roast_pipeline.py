from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.core.retrieval_config import RETRIEVAL_METHOD
from backend.services.retrieval.retriever_factory import get_retriever
from backend.services.roast.contradiction_finder import find_contradictions
from backend.services.roast.data_builder import build_user_data
from backend.services.roast.persona_analyzer import analyze_persona
from backend.services.roast.roast_writer import write_roast
from backend.services.roast.score_generator import generate_scores
from backend.services.roast.tag_generator import generate_tags


def _normalize_chunks(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []

    for i, r in enumerate(retrieved_chunks, start=1):
        chunks.append({
            "citation_id": r.get("citation_id", i),
            "doc_id": r.get("doc_id"),
            "chunk_id": r.get("chunk_id"),
            "chunk_index": r.get("chunk_index"),
            "content": r.get("content", ""),
            "page_start": r.get("page_start"),
            "page_end": r.get("page_end"),
            "section": r.get("section"),
            "metadata": r.get("metadata", {}),
        })

    return chunks


def _build_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    citations: List[Dict[str, Any]] = []

    for chunk in chunks:
        citations.append({
            "citation_id": chunk.get("citation_id"),
            "doc_id": chunk.get("doc_id"),
            "chunk_id": chunk.get("chunk_id"),
            "chunk_index": chunk.get("chunk_index"),
            "page_start": chunk.get("page_start"),
            "page_end": chunk.get("page_end"),
            "section": chunk.get("section"),
            "snippet": (chunk.get("content") or "")[:200],
        })

    return citations


def run_roast_pipeline(
    query: str,
    db: Session,
    document_ids: Optional[List[str]] = None,
    top_k: int = 6,
    method: Optional[str] = None,
    style_preference: Optional[str] = None,
    evidence_chunks: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    final_method = (method or RETRIEVAL_METHOD).strip()
    if final_method not in {"vector", "hybrid", "rerank"}:
        final_method = RETRIEVAL_METHOD

    if top_k <= 0:
        top_k = 6

    if evidence_chunks is not None:
        chunks = _normalize_chunks(evidence_chunks)
    else:
        retriever = get_retriever(final_method, db)
        retrieved_chunks = retriever.retrieve(
            question=query.strip(),
            document_ids=document_ids,
            top_k=top_k,
        )
        chunks = _normalize_chunks(retrieved_chunks)

    if not chunks:
        raise ValueError("No grounded evidence available for roast generation")

    user_data = build_user_data(
        chunks,
        query=query.strip(),
        document_ids=document_ids,
        top_k=top_k,
    )

    persona = analyze_persona(user_data)
    score_result = generate_scores(persona, user_data)
    tags = generate_tags(persona, user_data)
    contradictions = find_contradictions(persona, user_data)
    roast_text = write_roast(
        persona=persona,
        contradictions=contradictions,
        user_data=user_data,
        style_preference=style_preference,
    )

    citations = _build_citations(chunks)

    return {
        "query": query.strip(),
        "method": final_method,
        "persona": persona,
        "scores": score_result,
        "tags": tags,
        "contradictions": contradictions,
        "roast_text": roast_text,
        "citations": citations,
        "retrieval_count": len(chunks),
    }