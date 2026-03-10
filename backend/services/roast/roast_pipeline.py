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
    """
    把 retriever 返回的 chunk 统一整理成 build_user_data 可接受的结构。
    """
    chunks: List[Dict[str, Any]] = []

    for i, r in enumerate(retrieved_chunks, start=1):
        chunks.append(
            {
                "citation_id": r.get("citation_id", i),
                "doc_id": r.get("doc_id"),
                "chunk_id": r.get("chunk_id"),
                "chunk_index": r.get("chunk_index"),
                "content": r.get("content", ""),
                "page_start": r.get("page_start"),
                "page_end": r.get("page_end"),
                "section": r.get("section"),
                "metadata": r.get("metadata", {}),
            }
        )

    return chunks


def _build_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    从标准 chunk 结构构造 API 返回 citations。
    """
    citations: List[Dict[str, Any]] = []

    for chunk in chunks:
        citations.append(
            {
                "citation_id": chunk.get("citation_id"),
                "doc_id": chunk.get("doc_id"),
                "chunk_id": chunk.get("chunk_id"),
                "chunk_index": chunk.get("chunk_index"),
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
                "section": chunk.get("section"),
                "snippet": (chunk.get("content") or "")[:200],
            }
        )

    return citations


def run_roast_pipeline(
    query: str,
    db: Session,
    document_ids: Optional[List[str]] = None,
    top_k: int = 6,
    method: Optional[str] = None,
    style_preference: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Roast 主流程。

    步骤：
    1. Retrieval
    2. Build unified user_data payload
    3. Persona analysis
    4. Score generation
    5. Tag generation
    6. Contradiction finding
    7. Roast writing
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    final_method = (method or RETRIEVAL_METHOD).strip()

    # 兜底保护，避免传入非法 method 直接导致工厂报错
    if final_method not in {"vector", "hybrid", "rerank"}:
        final_method = RETRIEVAL_METHOD

    if top_k <= 0:
        top_k = 6

    retriever = get_retriever(final_method, db)

    retrieved_chunks = retriever.retrieve(
        question=query.strip(),
        document_ids=document_ids,
        top_k=top_k,
    )

    chunks = _normalize_chunks(retrieved_chunks)

    # 把 query / document_ids / top_k 一并写进统一 payload
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