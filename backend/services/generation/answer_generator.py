from pathlib import Path
from typing import List

from backend.services.llm.ollama_client import OllamaClient


class AnswerGenerator:
    """
    RAG回答生成模块

    职责：
    1. 从文件加载prompt模板
    2. 构建context
    3. 控制context长度
    4. 调用LLM生成回答
    """

    def __init__(self, model: str = "llama3.1:8b"):

        # 初始化本地LLM client
        self.client = OllamaClient(model=model)

        # 最大context长度（字符近似）
        self.max_context_chars = 12000

        # prompt文件路径
        self.prompt_path = (
            Path(__file__).parent / "prompts" / "answer_prompt.txt"
        )

    # --------------------------------------------------
    # 读取prompt模板
    # --------------------------------------------------

    def load_prompt_template(self) -> str:
        """
        从文件加载prompt模板
        """

        with open(self.prompt_path, "r", encoding="utf-8") as f:
            template = f.read()

        return template

    # --------------------------------------------------
    # 构建context
    # --------------------------------------------------

    def build_context(self, chunks: List[dict]) -> str:
        """
        将retriever返回的chunk拼接为context
        """

        context_parts = []

        for c in chunks:

            text = f"[{c['citation_id']}] {c['content']}"

            context_parts.append(text)

        context = "\n\n".join(context_parts)

        return context

    # --------------------------------------------------
    # 控制context长度
    # --------------------------------------------------

    def truncate_context(self, context: str) -> str:
        """
        防止context过长
        """

        if len(context) <= self.max_context_chars:
            return context

        return context[: self.max_context_chars]

    # --------------------------------------------------
    # 构造prompt
    # --------------------------------------------------

    def build_prompt(self, question: str, chunks: List[dict]) -> str:

        template = self.load_prompt_template()

        context = self.build_context(chunks)

        context = self.truncate_context(context)

        prompt = template.format(
            context=context,
            question=question
        )

        return prompt

    # --------------------------------------------------
    # 生成回答
    # --------------------------------------------------

    def generate(self, question: str, chunks: List[dict]) -> str:
        """
        调用LLM生成回答
        """

        prompt = self.build_prompt(question, chunks)

        system_prompt = (
            "You are a helpful assistant that answers questions "
            "using provided context and cites sources like [1], [2]."
        )

        answer = self.client.chat(
            system=system_prompt,
            user=prompt
        )

        return answer