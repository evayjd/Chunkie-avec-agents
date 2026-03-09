import json
import re

from backend.services.llm.ollama_client import OllamaClient


class Agent:
    """
    完整版单步 Agent

    流程：
    1. 读取可用 tools
    2. 让 LLM 选择 tool + arguments
    3. 执行 tool
    4. 让 LLM 根据 tool output 生成最终回答
    """

    def __init__(self, registry, executor):
        self.registry = registry
        self.executor = executor
        self.llm = OllamaClient()

    def _build_tool_prompt(self, question: str, method: str, top_k: int, document_ids):
        tool_specs = self.registry.get_tool_specs()

        tools_text = json.dumps(tool_specs, ensure_ascii=False, indent=2)

        return f"""
You are an agent that chooses the best tool for the user's request.

Available tools:
{tools_text}

User question:
{question}

Global defaults:
- method = "{method}"
- top_k = {top_k}
- document_ids = {document_ids}

Rules:
- Use rag_search_tool when the user seems to want raw evidence or retrieval only.
- Use answer_tool for normal document QA.
- Use document_summary_tool when the user asks to summarize a document.
- Use document_compare_tool when the user asks to compare documents.
- Use roast_tool when the user asks for a roast.

Return ONLY valid JSON in this format:
{{
  "tool": "tool_name",
  "arguments": {{
    "question": "...",
    "method": "{method}",
    "top_k": {top_k},
    "document_ids": {document_ids}
  }}
}}
"""

    def _extract_json(self, text: str):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None

        try:
            return json.loads(match.group())
        except Exception:
            return None

    def _format_final_answer(self, question: str, tool_name: str, tool_result):
        prompt = f"""
You are a helpful assistant.

The user asked:
{question}

The tool used was:
{tool_name}

The tool result is:
{json.dumps(tool_result, ensure_ascii=False, indent=2)}

Generate a final user-facing response.
Rules:
- Be concise but helpful
- If the tool already contains a final answer, present it clearly
- If citations are present, preserve them in the response structure if possible
"""

        return self.llm.generate(prompt)

    def run(
        self,
        question: str,
        method: str = "hybrid",
        top_k: int = 5,
        document_ids=None
    ):
        routing_prompt = self._build_tool_prompt(
            question=question,
            method=method,
            top_k=top_k,
            document_ids=document_ids
        )

        routing_response = self.llm.generate(routing_prompt)

        decision = self._extract_json(routing_response)

        if not decision:
            # fallback
            tool_name = "answer_tool"
            arguments = {
                "question": question,
                "method": method,
                "top_k": top_k,
                "document_ids": document_ids
            }
        else:
            tool_name = decision.get("tool", "answer_tool")
            arguments = decision.get("arguments", {})

            # 补齐默认参数
            if "question" not in arguments and tool_name in {"rag_search_tool", "answer_tool"}:
                arguments["question"] = question
            if "method" not in arguments:
                arguments["method"] = method
            if "top_k" not in arguments and tool_name in {"rag_search_tool", "answer_tool"}:
                arguments["top_k"] = top_k
            if "document_ids" not in arguments and tool_name in {"rag_search_tool", "answer_tool"}:
                arguments["document_ids"] = document_ids

        tool_result = self.executor.execute(tool_name, arguments)

        final_answer = self._format_final_answer(
            question=question,
            tool_name=tool_name,
            tool_result=tool_result
        )

        return {
            "tool_used": tool_name,
            "tool_arguments": arguments,
            "tool_result": tool_result,
            "final_answer": final_answer
        }