# test_tool.py

from backend.services.agent.tools.rag_search_tool import RagSearchTool

tool = RagSearchTool()

result = tool.run(
    question="What is this document about?",
    method="rerank"
)

print(result)