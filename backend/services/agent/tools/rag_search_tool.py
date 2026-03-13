from typing import List, Optional

from sqlalchemy.orm import Session

from backend.services.citations.citation_builder import CitationBuilder
from backend.services.retrieval.retriever_factory import get_retriever


class RagSearchTool:
    name = "rag_search_tool"
    description = "Search relevant document chunks for a question without generating a final answer."
    input_schema = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "minLength": 1
            },
            "method": {
                "type": "string",
                "enum": ["vector", "hybrid", "rerank"],
                "default": "hybrid"
            },
            "top_k": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "default": 5
            },
            "document_ids": {
                "type": ["array", "null"],
                "items": {"type": "string"}
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }

    def __init__(self, db: Session):
        self.db = db
        self.citation_builder = CitationBuilder()

    def run(
        self,
        question: str,
        method: str = "hybrid",
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
    ):
        retriever = get_retriever(method, self.db)
        chunks = retriever.retrieve(
            question=question,
            document_ids=document_ids,
            top_k=top_k,
        )
        citations = self.citation_builder.build_citations(chunks)

        return {
            "question": question,
            "method": method,
            "top_k": top_k,
            "document_ids": document_ids,
            "chunks": chunks,
            "citations": citations,
            "retrieval_count": len(chunks),
        }