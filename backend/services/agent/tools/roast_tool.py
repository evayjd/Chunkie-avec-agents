from typing import List, Optional

from sqlalchemy.orm import Session

from backend.services.roast.roast_pipeline import run_roast_pipeline


class RoastTool:
    name = "roast_tool"
    description = "Generate a persona-style roast analysis grounded in audited uploaded document evidence."
    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "minLength": 1,
                "description": "Roast analysis query or target description."
            },
            "target_id": {
                "type": "string",
                "minLength": 1,
                "description": "Primary target document id."
            },
            "document_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional document ids to constrain roast retrieval."
            },
            "top_k": {
                "type": "integer",
                "minimum": 1,
                "maximum": 20,
                "default": 6
            },
            "method": {
                "type": "string",
                "enum": ["vector", "hybrid", "rerank"],
                "default": "rerank"
            },
            "style_preference": {
                "type": "string",
                "minLength": 1,
                "default": "sharp_witty"
            },
            "evidence_chunks": {
                "type": ["array", "null"],
                "items": {"type": "object"},
                "description": "Audited retrieval chunks injected by the workflow agent."
            }
        },
        "required": ["query", "target_id", "style_preference"],
        "additionalProperties": False
    }

    def __init__(self, db: Session):
        self.db = db

    def run(
        self,
        query: str,
        target_id: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 6,
        method: str = "rerank",
        style_preference: str = "sharp_witty",
        evidence_chunks: Optional[List[dict]] = None,
    ):
        scoped_document_ids = document_ids or [target_id]

        return run_roast_pipeline(
            query=query,
            db=self.db,
            document_ids=scoped_document_ids,
            top_k=top_k,
            method=method,
            style_preference=style_preference,
            evidence_chunks=evidence_chunks,
        )