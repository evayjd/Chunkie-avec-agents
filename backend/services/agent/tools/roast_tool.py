import requests


class RoastTool:
    name = "roast_tool"
    description = "Generate a persona-style roast analysis grounded in uploaded documents."
    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Roast analysis query or target description."
            },
            "document_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional document ids to constrain roast retrieval."
            },
            "top_k": {
                "type": "integer",
                "default": 6
            },
            "method": {
                "type": "string",
                "enum": ["vector", "hybrid", "rerank"],
                "default": "rerank"
            },
            "style_preference": {
                "type": "string",
                "description": "Optional roast style preference."
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def run(
        self,
        query: str,
        document_ids=None,
        top_k: int = 6,
        method: str = "rerank",
        style_preference: str | None = None
    ):
        """
        RoastTool 把 query 一并传给 /roast，
        """
        response = requests.post(
            f"{self.base_url}/roast",
            json={
                "query": query,
                "document_ids": document_ids,
                "top_k": top_k,
                "method": method,
                "style_preference": style_preference,
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json()