import json
import re
from typing import Any, Dict, List, Optional, Sequence, Union

import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"


class RoastLLMError(Exception):
    pass


class RoastUserPayload(dict):
    """
    Dict-like payload for roast pipeline.

    Why this exists:
    - roast_pipeline currently passes user_data into multiple prompt builders
    - some downstream code implicitly treats user_data as printable text
    - this class keeps machine-readable dict semantics while providing a stable
      string representation for prompt construction
    """

    def to_prompt_text(self) -> str:
        return json.dumps(self, ensure_ascii=False, indent=2)

    def __str__(self) -> str:
        return self.to_prompt_text()


def _extract_json(text: str) -> Dict[str, Any]:
    """
    Try to extract a JSON object from model output.
    """

    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    raise RoastLLMError("LLM output is not valid JSON")


def chat(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {
            "temperature": temperature,
        },
        "stream": False,
    }

    res = requests.post(OLLAMA_URL, json=payload, timeout=120)

    if res.status_code != 200:
        raise RoastLLMError(res.text)

    return res.json()["message"]["content"]


def chat_json(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    text = chat(system_prompt, user_prompt)
    return _extract_json(text)


def chat_text(system_prompt: str, user_prompt: str) -> str:
    return chat(system_prompt, user_prompt, temperature=0.9)


def safe_list(items: List[Any], max_len: int = 6) -> List[str]:
    if not isinstance(items, list):
        return []

    cleaned: List[str] = []

    for i in items:
        if isinstance(i, str):
            value = i.strip()
            if value:
                cleaned.append(value)

    return cleaned[:max_len]


def clamp_score(x: Any) -> int:
    try:
        x = int(float(x))
    except Exception:
        return 50

    return max(0, min(100, x))


def clamp_rate(x: Any) -> float:
    try:
        x = round(float(x), 1)
    except Exception:
        return 90.0

    return max(80.0, min(99.0, x))


# -------------------------------------------------------------------
# Contract normalization
# -------------------------------------------------------------------

ParsedDoc = Dict[str, Any]
ChunkLike = Dict[str, Any]
UserDataInput = Union[ParsedDoc, Sequence[ChunkLike]]


def _is_parsed_doc(obj: Any) -> bool:
    """
    Stable ingestion contract:
    {
        "text": str,
        "pages": list[dict],
        "metadata": dict
    }
    """
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
    """
    Unified roast evidence chunk contract.

    Accepted upstream variants:
    1. Retrieval output:
       {
         "citation_id", "doc_id", "chunk_id", "chunk_index",
         "content", "page_start", "page_end", "section"
       }

    2. Ingestion chunk output:
       {
         "chunk_id", "chunk_index", "content",
         "page_start", "page_end", "section", "metadata"
       }
    """
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
    pages: List[Dict[str, Any]] = [
        _normalize_page(page, fallback_num=i)
        for i, page in enumerate(raw_pages, start=1)
    ]

    evidence_chunks: List[Dict[str, Any]] = []

    for i, page in enumerate(pages, start=1):
        content = (page.get("content") or "").strip()
        if not content:
            continue

        evidence_chunks.append(
            {
                "citation_id": i,
                "doc_id": None,
                "chunk_id": None,
                "chunk_index": i - 1,
                "content": content,
                "page_start": page["page_num"],
                "page_end": page["page_num"],
                "section": page.get("section"),
                "metadata": {},
            }
        )

    evidence_texts = [c["content"] for c in evidence_chunks if c["content"].strip()]
    full_text = str(parsed_doc.get("text", "") or "")

    payload = RoastUserPayload(
        {
            "schema_version": "1.0",
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
        }
    )

    return payload


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

    payload = RoastUserPayload(
        {
            "schema_version": "1.0",
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
        }
    )

    return payload


def build_user_data(
    source: UserDataInput,
    query: Optional[str] = None,
    document_ids: Optional[List[str]] = None,
    top_k: Optional[int] = None,
) -> RoastUserPayload:
    """
    Build a unified roast payload from either:
    1. ingestion parsed_doc dict
    2. retrieval / roast_pipeline chunk list

    Output contract (100% fixed):
    {
        "schema_version": str,
        "source_type": "parsed_doc" | "retrieved_chunks",
        "query": str | None,
        "document_ids": List[str],
        "top_k": int | None,
        "full_text": str,
        "metadata": Dict[str, Any],
        "pages": List[
            {
                "page_num": int,
                "content": str,
                "section": str | None
            }
        ],
        "evidence_chunks": List[
            {
                "citation_id": int,
                "doc_id": str | None,
                "chunk_id": str | None,
                "chunk_index": int | None,
                "content": str,
                "page_start": int | None,
                "page_end": int | None,
                "section": str | None,
                "metadata": Dict[str, Any]
            }
        ],
        "evidence_texts": List[str],
        "stats": {
            "page_count": int,
            "evidence_chunk_count": int,
            "text_char_count": int
        }
    }

    This function is intentionally shape-stable so that roast_pipeline and all
    downstream roast prompts consume the same payload regardless of whether the
    source is parsed_doc or retrieved chunks.
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