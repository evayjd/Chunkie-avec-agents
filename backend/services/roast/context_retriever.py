from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from backend.core.retrieval_config import RETRIEVAL_METHOD
from backend.services.retrieval.retriever_factory import get_retriever


def retrieve_roast_context(
    query: str,
    db: Session,
    document_ids: Optional[List[str]] = None,
    top_k: int = 6,
) -> List[Dict[str, Any]]:
    """
    Retrieve chunks for roast analysis.

    This function reuses the project's existing retrieval pipeline
    (vector / hybrid / rerank), based on RETRIEVAL_METHOD.

    Returns a normalized list of chunk dictionaries:
    [
        {
            "citation_id": int,
            "doc_id": str,
            "chunk_id": str,
            "chunk_index": int,
            "content": str,
            "page_start": int | None,
            "page_end": int | None,
            "section": str | None
        }
    ]
    """

    if not query or not query.strip():
        return []

    if top_k <= 0:
        top_k = 6

    retriever = get_retriever(RETRIEVAL_METHOD, db)

    chunks = retriever.retrieve(
        question=query.strip(),
        document_ids=document_ids,
        top_k=top_k,
    )

    normalized_chunks: List[Dict[str, Any]] = []

    for i, chunk in enumerate(chunks, start=1):
        normalized_chunks.append(
            {
                "citation_id": chunk.get("citation_id", i),
                "doc_id": chunk.get("doc_id"),
                "chunk_id": chunk.get("chunk_id"),
                "chunk_index": chunk.get("chunk_index"),
                "content": chunk.get("content", ""),
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
                "section": chunk.get("section"),
            }
        )

    return normalized_chunks


def retrieve_roast_texts(
    query: str,
    db: Session,
    document_ids: Optional[List[str]] = None,
    top_k: int = 6,
) -> List[str]:
    """
    Retrieve only chunk texts for roast prompt building.
    """

    chunks = retrieve_roast_context(
        query=query,
        db=db,
        document_ids=document_ids,
        top_k=top_k,
    )

    texts: List[str] = []

    for chunk in chunks:
        content = (chunk.get("content") or "").strip()
        if content:
            texts.append(content)

    return texts