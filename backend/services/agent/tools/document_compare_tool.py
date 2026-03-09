from backend.services.llm.ollama_client import OllamaClient
from backend.services.agent.tools.rag_search_tool import RagSearchTool


class DocumentCompareTool:
    name = "document_compare_tool"
    description = "Compare two or more documents by retrieving relevant chunks and summarizing similarities/differences."
    input_schema = {
        "document_ids": "list[string]",
        "method": "string"
    }

    def __init__(self):
        self.search_tool = RagSearchTool()
        self.llm = OllamaClient()

    def run(
        self,
        document_ids,
        method: str = "hybrid"
    ):
        all_context = []

        for doc_id in document_ids:
            retrieval = self.search_tool.run(
                question="What is this document mainly about?",
                method=method,
                top_k=6,
                document_ids=[doc_id]
            )

            citations = retrieval.get("citations", [])
            snippets = "\n".join(c.get("snippet", "") for c in citations)

            all_context.append(
                f"Document {doc_id}:\n{snippets}"
            )

        combined_context = "\n\n".join(all_context)

        prompt = f"""
Compare the following documents.

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
            "comparison": comparison
        }