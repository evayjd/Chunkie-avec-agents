from typing import List, Optional

from sqlalchemy.orm import Session

from backend.services.generation.answer_generator import AnswerGenerator
from backend.services.llm.ollama_client import OllamaClient
from backend.services.retrieval.retriever_factory import get_retriever
from backend.services.citations.citation_builder import CitationBuilder


class AnswerTool:
    name = "answer_tool"
    description = "Answer a question using the RAG pipeline, or general knowledge when explicitly allowed."
    input_schema = {
        "type": "object",
        "properties": {
            "question": {"type": "string", "minLength": 1},
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
            },
            "use_general_knowledge": {
                "type": "boolean",
                "default": False
            },
            "fallback_notice": {
                "type": ["string", "null"]
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }

    def __init__(self, db: Session):
        self.db = db
        self.generator = AnswerGenerator()
        self.llm = OllamaClient()
        self.citation_builder = CitationBuilder()

    def run(
        self,
        question: str,
        method: str = "hybrid",
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        use_general_knowledge: bool = False,
        fallback_notice: Optional[str] = None,
    ):
        if use_general_knowledge:
            prompt = f"""
Answer the question using general knowledge only.
Do not pretend the answer is grounded in uploaded files.
Be explicit if certainty is limited.

Question:
{question}
"""
            answer = self.llm.generate(prompt)
            return {
                "answer": answer,
                "citations": [],
                "used_general_knowledge": True,
                "fallback_notice": fallback_notice,
            }

        retriever = get_retriever(method, self.db)
        chunks = retriever.retrieve(
            question=question,
            document_ids=document_ids,
            top_k=top_k,
        )
        answer = self.generator.generate(question, chunks)
        citations = self.citation_builder.build_citations(chunks)

        return {
            "answer": answer,
            "citations": citations,
            "used_general_knowledge": False,
            "fallback_notice": fallback_notice,
        }