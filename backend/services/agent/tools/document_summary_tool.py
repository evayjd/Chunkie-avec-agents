from typing import List, Optional

from sqlalchemy.orm import Session

from backend.services.llm.ollama_client import OllamaClient
from backend.services.agent.tools.rag_search_tool import RagSearchTool


class DocumentSummaryTool:
    name = "document_summary_tool"
    description = "Summarize a specific document using audited or freshly retrieved chunks."
    input_schema = {
        "type": "object",
        "properties": {
            "target_id": {
                "type": "string",
                "minLength": 1,
                "description": "Target document id to summarize."
            },
            "method": {
                "type": "string",
                "enum": ["vector", "hybrid", "rerank"],
                "default": "hybrid"
            },
            "top_k": {
                "type": "integer",
                "minimum": 1,
                "maximum": 20,
                "default": 8
            },
            "style_preference": {
                "type": "string",
                "default": "concise_brief"
            },
            "evidence_chunks": {
                "type": ["array", "null"],
                "items": {"type": "object"}
            }
        },
        "required": ["target_id"],
        "additionalProperties": False
    }

    def __init__(self, db: Session):
        self.search_tool = RagSearchTool(db)
        self.llm = OllamaClient()

    def run(
        self,
        target_id: str,
        method: str = "hybrid",
        top_k: int = 8,
        style_preference: str = "concise_brief",
        evidence_chunks: Optional[List[dict]] = None,
    ):
        if evidence_chunks is None:
            retrieval = self.search_tool.run(
                question="Summarize the document.",
                method=method,
                top_k=top_k,
                document_ids=[target_id],
            )
            citations = retrieval.get("citations", [])
        else:
            citations = []
            for i, c in enumerate(evidence_chunks, start=1):
                citations.append({
                    "citation_id": c.get("citation_id", i),
                    "doc_id": c.get("doc_id"),
                    "chunk_id": c.get("chunk_id"),
                    "chunk_index": c.get("chunk_index"),
                    "page_start": c.get("page_start"),
                    "page_end": c.get("page_end"),
                    "section": c.get("section"),
                    "snippet": (c.get("content") or "")[:200],
                })

        context = "\n\n".join(c.get("snippet", "") for c in citations)

        prompt = f"""
Summarize the following document excerpts.

Style preference: {style_preference}

Requirements:
- concise but informative
- mention the main themes
- mention notable details if present
- stay grounded in the provided context only

Context:
{context}
"""

        summary = self.llm.generate(prompt)

        return {
            "target_id": target_id,
            "style_preference": style_preference,
            "summary": summary,
            "citations": citations,
        }