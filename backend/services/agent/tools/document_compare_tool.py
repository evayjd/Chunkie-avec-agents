from typing import List

from sqlalchemy.orm import Session

from backend.services.llm.ollama_client import OllamaClient
from backend.services.agent.tools.rag_search_tool import RagSearchTool


class DocumentCompareTool:
    name = "document_compare_tool"
    description = "Compare two or more documents by retrieving relevant chunks and summarizing similarities/differences."
    input_schema = {
        "type": "object",
        "properties": {
            "document_ids": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "description": "Two or more document ids to compare."
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
                "default": 6
            },
            "style_preference": {
                "type": "string",
                "default": "contrastive_structured"
            }
        },
        "required": ["document_ids"],
        "additionalProperties": False
    }

    def __init__(self, db: Session):
        self.search_tool = RagSearchTool(db)
        self.llm = OllamaClient()

    def run(
        self,
        document_ids: List[str],
        method: str = "hybrid",
        top_k: int = 6,
        style_preference: str = "contrastive_structured",
    ):
        all_context = []
        all_citations = []

        for doc_id in document_ids:
            retrieval = self.search_tool.run(
                question="What is this document mainly about?",
                method=method,
                top_k=top_k,
                document_ids=[doc_id],
            )

            citations = retrieval.get("citations", [])
            all_citations.extend(citations)
            snippets = "\n".join(c.get("snippet", "") for c in citations)

            all_context.append(f"Document {doc_id}:\n{snippets}")

        combined_context = "\n\n".join(all_context)

        prompt = f"""
Compare the following documents.

Style preference: {style_preference}

Requirements:
- identify similarities
- identify differences
- mention themes, topics, or style differences if visible
- be grounded only in the provided context

Context:
{combined_context}
"""

        comparison = self.llm.generate(prompt)

        return {
            "document_ids": document_ids,
            "style_preference": style_preference,
            "comparison": comparison,
            "citations": all_citations,
        }