import json
from typing import Any, Dict, List, Optional, Sequence, Union


class RoastUserPayload(dict):
    """
    Stable dict-like payload for roast pipeline.
    """

    def to_prompt_text(self) -> str:
        return json.dumps(self, ensure_ascii=False, indent=2)

    def __str__(self) -> str:
        return self.to_prompt_text()


ParsedDoc = Dict[str, Any]
ChunkLike = Dict[str, Any]
UserDataInput = Union[ParsedDoc, Sequence[ChunkLike]]


def _is_parsed_doc(obj: Any) -> bool:
    return (
        isinstance(obj, dict)
        and "text" in obj
        and "pages" in obj
        and isinstance(obj.get("pages"), list)
    )


def _is_chunk_list(obj: Any) -> bool:
    return isinstance(obj, list)


def _normalize_page(page: Dict[str, Any], fallback_num: int) -> Dict[str, Any]:
    return {
        "page_num": int(page.get("page_num", fallback_num)),
        "content": str(page.get("content", "") or ""),
        "section": page.get("section"),
    }


def _normalize_chunk(chunk: Dict[str, Any], fallback_citation_id: int) -> Dict[str, Any]:
    return {
        "citation_id": int(chunk.get("citation_id", fallback_citation_id)),
        "doc_id": chunk.get("doc_id"),
        "chunk_id": chunk.get("chunk_id"),
        "chunk_index": chunk.get("chunk_index"),
        "content": str(chunk.get("content", "") or ""),
        "page_start": chunk.get("page_start"),
        "page_end": chunk.get("page_end"),
        "section": chunk.get("section"),
        "metadata": chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {},
    }


def _build_from_parsed_doc(
    parsed_doc: ParsedDoc,
    query: Optional[str] = None,
    document_ids: Optional[List[str]] = None,
    top_k: Optional[int] = None,
) -> RoastUserPayload:
    raw_pages = parsed_doc.get("pages", []) or []
    pages = [
        _normalize_page(page, fallback_num=i)
        for i, page in enumerate(raw_pages, start=1)
    ]

    evidence_chunks: List[Dict[str, Any]] = []

    for i, page in enumerate(pages, start=1):
        content = (page.get("content") or "").strip()
        if not content:
            continue

        evidence_chunks.append({
            "citation_id": i,
            "doc_id": None,
            "chunk_id": None,
            "chunk_index": i - 1,
            "content": content,
            "page_start": page["page_num"],
            "page_end": page["page_num"],
            "section": page.get("section"),
            "metadata": {},
        })

    full_text = str(parsed_doc.get("text", "") or "")
    evidence_texts = [c["content"] for c in evidence_chunks if c["content"].strip()]

    return RoastUserPayload({
        "schema_version": "2.0",
        "source_type": "parsed_doc",
        "query": query,
        "document_ids": document_ids or [],
        "top_k": top_k,
        "full_text": full_text,
        "metadata": parsed_doc.get("metadata") if isinstance(parsed_doc.get("metadata"), dict) else {},
        "pages": pages,
        "evidence_chunks": evidence_chunks,
        "evidence_texts": evidence_texts,
        "stats": {
            "page_count": len(pages),
            "evidence_chunk_count": len(evidence_chunks),
            "text_char_count": len(full_text),
        },
    })


def _build_from_chunks(
    chunks: Sequence[ChunkLike],
    query: Optional[str] = None,
    document_ids: Optional[List[str]] = None,
    top_k: Optional[int] = None,
) -> RoastUserPayload:
    normalized_chunks: List[Dict[str, Any]] = []
    pages_map: Dict[int, Dict[str, Any]] = {}
    inferred_doc_ids: List[str] = []

    for i, chunk in enumerate(chunks, start=1):
        norm = _normalize_chunk(chunk, fallback_citation_id=i)
        normalized_chunks.append(norm)

        doc_id = norm.get("doc_id")
        if isinstance(doc_id, str) and doc_id not in inferred_doc_ids:
            inferred_doc_ids.append(doc_id)

        page_start = norm.get("page_start")
        if isinstance(page_start, int) and page_start not in pages_map:
            pages_map[page_start] = {
                "page_num": page_start,
                "content": norm["content"],
                "section": norm.get("section"),
            }

    pages = [pages_map[k] for k in sorted(pages_map.keys())]
    evidence_texts = [c["content"] for c in normalized_chunks if c["content"].strip()]
    full_text = "\n\n".join(evidence_texts)

    return RoastUserPayload({
        "schema_version": "2.0",
        "source_type": "retrieved_chunks",
        "query": query,
        "document_ids": document_ids or inferred_doc_ids,
        "top_k": top_k,
        "full_text": full_text,
        "metadata": {},
        "pages": pages,
        "evidence_chunks": normalized_chunks,
        "evidence_texts": evidence_texts,
        "stats": {
            "page_count": len(pages),
            "evidence_chunk_count": len(normalized_chunks),
            "text_char_count": len(full_text),
        },
    })


def build_user_data(
    source: UserDataInput,
    query: Optional[str] = None,
    document_ids: Optional[List[str]] = None,
    top_k: Optional[int] = None,
) -> RoastUserPayload:
    """
    Stable contract for roast pipeline.

    Supports:
    1. parsed_doc
    2. retrieved chunks
    """
    if _is_parsed_doc(source):
        return _build_from_parsed_doc(
            parsed_doc=source,
            query=query,
            document_ids=document_ids,
            top_k=top_k,
        )

    if _is_chunk_list(source):
        return _build_from_chunks(
            chunks=source,
            query=query,
            document_ids=document_ids,
            top_k=top_k,
        )

    raise TypeError(
        "build_user_data expects either a parsed_doc dict or a list of chunk dictionaries."
    )