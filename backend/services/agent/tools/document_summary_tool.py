from backend.services.llm.ollama_client import OllamaClient
from backend.services.agent.tools.rag_search_tool import RagSearchTool


class DocumentSummaryTool:
    name = "document_summary_tool"
    description = "Summarize a specific document using retrieved chunks."
    input_schema = {
        "document_id": "string",
        "method": "string"
    }

    def __init__(self):
        self.search_tool = RagSearchTool()
        self.llm = OllamaClient()

    def run(
        self,
        document_id: str,
        method: str = "hybrid"
    ):
        retrieval = self.search_tool.run(
            question="Summarize the document.",
            method=method,
            top_k=8,
            document_ids=[document_id]
        )

        citations = retrieval.get("citations", [])

        context = "\n\n".join(
            c.get("snippet", "") for c in citations
        )

        prompt = f"""
Summarize the following document excerpts.

Requirements:
- concise but informative
- mention the main themes
- mention notable details if present

Context:
{context}
"""

        summary = self.llm.generate(prompt)

        return {
            "document_id": document_id,
            "summary": summary,
            "citations": citations
        }