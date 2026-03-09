from backend.services.agent.agent import Agent
from backend.services.agent.tool_registry import ToolRegistry
from backend.services.agent.agent_executor import AgentExecutor

from backend.services.agent.tools.rag_search_tool import RagSearchTool
from backend.services.agent.tools.answer_tool import AnswerTool


def main():

    registry = ToolRegistry()

    registry.register(RagSearchTool())
    registry.register(AnswerTool())

    executor = AgentExecutor(registry)

    agent = Agent(registry, executor)

    result = agent.run(
        question="What is this document about?"
    )

    print(result)


if __name__ == "__main__":
    main()