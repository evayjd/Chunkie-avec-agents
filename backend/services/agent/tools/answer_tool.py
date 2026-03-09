import requests


class AnswerTool:
    name = "answer_tool"
    description = "Answer a question using the RAG pipeline."
    input_schema = {
        "question": "string",
        "method": "string",
        "top_k": "integer",
        "document_ids": "list[string] | null"
    }

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def run(
        self,
        question: str,
        method: str = "hybrid",
        top_k: int = 5,
        document_ids=None
    ):
        response = requests.post(
            f"{self.base_url}/ask",
            json={
                "question": question,
                "method": method,
                "top_k": top_k,
                "document_ids": document_ids
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json()