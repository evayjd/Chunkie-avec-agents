import json
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.services.llm.ollama_client import OllamaClient


class Agent:
    """
    Single-step agent with:
    1. LLM routing
    2. Pre-flight parameter injection
    3. Retrieval verifier and retry
    4. Context-gated fallback
    """

    CONTEXT_REQUIRED_TOOLS = {
        "roast_tool",
        "document_summary_tool",
        "document_compare_tool",
    }

    def __init__(self, registry, executor):
        self.registry = registry
        self.executor = executor
        self.llm = OllamaClient()

    # ------------------------------------------------------------------
    # Prompting
    # ------------------------------------------------------------------

    def _build_tool_prompt(
        self,
        question: str,
        method: str,
        top_k: int,
        document_ids: Optional[List[str]],
    ) -> str:
        tool_specs = self.registry.get_tool_specs()
        tools_text = json.dumps(tool_specs, ensure_ascii=False, indent=2)

        return f"""
You are an orchestration agent.

You must choose exactly one tool and return ONLY valid JSON.

Available tools:
{tools_text}

User question:
{question}

Global defaults:
- method = "{method}"
- top_k = {top_k}
- document_ids = {document_ids}

Critical routing rules:
- Use rag_search_tool for retrieval-only requests.
- Use answer_tool for normal QA.
- Use document_summary_tool only when a concrete target document can be identified.
- Use document_compare_tool only when 2 or more documents are in scope.
- Use roast_tool only when the user explicitly asks for a roast / persona teardown / humorous critique.
- Do not invent parameters that violate the schema.
- Prefer carrying over provided document_ids when relevant.

Return JSON only:
{{
  "tool": "tool_name",
  "arguments": {{}}
}}
"""

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None

        try:
            return json.loads(match.group())
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Parameter injection
    # ------------------------------------------------------------------

    def _extract_uuid_candidates(self, text: str) -> List[str]:
        pattern = r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
        return re.findall(pattern, text or "")

    def _infer_target_id(
        self,
        question: str,
        document_ids: Optional[List[str]],
        arguments: Dict[str, Any],
    ) -> Optional[str]:
        if isinstance(arguments.get("target_id"), str) and arguments["target_id"].strip():
            return arguments["target_id"].strip()

        if isinstance(arguments.get("document_id"), str) and arguments["document_id"].strip():
            return arguments["document_id"].strip()

        mentioned = self._extract_uuid_candidates(question)
        if mentioned:
            return mentioned[0]

        if document_ids and len(document_ids) == 1:
            return document_ids[0]

        return None

    def _inject_missing_parameters(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        question: str,
        method: str,
        top_k: int,
        document_ids: Optional[List[str]],
    ) -> Dict[str, Any]:
        args = dict(arguments or {})

        # Shared defaults
        args.setdefault("method", method)

        # QA / retrieval
        if tool_name in {"rag_search_tool", "answer_tool"}:
            args.setdefault("question", question)
            args.setdefault("top_k", top_k)
            args.setdefault("document_ids", document_ids)

        # Summary
        elif tool_name == "document_summary_tool":
            target_id = self._infer_target_id(question, document_ids, args)
            if target_id and "document_id" not in args:
                args["document_id"] = target_id

        # Compare
        elif tool_name == "document_compare_tool":
            if "document_ids" not in args or not isinstance(args.get("document_ids"), list):
                args["document_ids"] = document_ids or []

        # Roast
        elif tool_name == "roast_tool":
            args.setdefault("query", question)
            args.setdefault("document_ids", document_ids)
            args.setdefault("top_k", max(top_k, 6))
            args.setdefault("style_preference", "sharp_witty")

            target_id = self._infer_target_id(question, document_ids, args)
            if target_id:
                args.setdefault("target_id", target_id)

            # Optional normalization:
            # if target_id exists but document_ids is empty, scope roast to that target
            if (not args.get("document_ids")) and args.get("target_id"):
                args["document_ids"] = [args["target_id"]]

        return args

    # ------------------------------------------------------------------
    # Retrieval verifier
    # ------------------------------------------------------------------

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]+", (text or "").lower())
        return [t for t in tokens if len(t) >= 2]

    def _verify_retrieval_result(
        self,
        question: str,
        retrieval_result: Dict[str, Any],
        threshold: float = 0.7,
    ) -> Dict[str, Any]:
        citations = retrieval_result.get("citations", []) if isinstance(retrieval_result, dict) else []

        if not citations:
            return {
                "ok": False,
                "score": 0.0,
                "reason": "empty",
                "citations_found": 0,
            }

        question_tokens = set(self._tokenize(question))
        if not question_tokens:
            return {
                "ok": False,
                "score": 0.0,
                "reason": "empty_question_tokens",
                "citations_found": len(citations),
            }

        snippet_scores: List[float] = []

        for c in citations:
            snippet = c.get("snippet", "") or c.get("content", "") or ""
            snippet_tokens = set(self._tokenize(snippet))

            if not snippet_tokens:
                snippet_scores.append(0.0)
                continue

            overlap = len(question_tokens & snippet_tokens)
            precision = overlap / max(1, len(snippet_tokens))
            recall = overlap / max(1, len(question_tokens))

            # Balanced lexical relevance proxy in [0, 1]
            score = (0.55 * recall) + (0.45 * precision)
            snippet_scores.append(score)

        best_score = max(snippet_scores) if snippet_scores else 0.0
        avg_score = sum(snippet_scores) / len(snippet_scores) if snippet_scores else 0.0
        final_score = round((0.7 * best_score) + (0.3 * avg_score), 3)

        return {
            "ok": final_score >= threshold,
            "score": final_score,
            "reason": "passed" if final_score >= threshold else "below_threshold",
            "citations_found": len(citations),
        }

    def _relax_query(self, question: str) -> str:
        """
        Second-pass query relaxation.
        - strips punctuation
        - removes common function words
        - keeps content-bearing tokens only
        """
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "to", "of", "for", "and",
            "or", "in", "on", "with", "about", "what", "which", "who", "why", "how",
            "请", "帮我", "一下", "关于", "这个", "那个", "什么", "怎么", "如何", "一下子",
        }

        tokens = self._tokenize(question)
        relaxed = [t for t in tokens if t not in stopwords]

        if not relaxed:
            return question.strip()

        return " ".join(relaxed[:10]).strip()

    def _probe_context(
        self,
        question: str,
        method: str,
        top_k: int,
        document_ids: Optional[List[str]],
    ) -> Dict[str, Any]:
        first_pass = self.executor.execute(
            "rag_search_tool",
            {
                "question": question,
                "method": method,
                "top_k": max(top_k, 6),
                "document_ids": document_ids,
            },
        )

        verdict = self._verify_retrieval_result(question, first_pass, threshold=0.7)
        if verdict["ok"]:
            return {
                "ok": True,
                "stage": "first_pass",
                "verdict": verdict,
                "retrieval_result": first_pass,
            }

        relaxed_question = self._relax_query(question)

        second_pass = self.executor.execute(
            "rag_search_tool",
            {
                "question": relaxed_question,
                "method": method,
                "top_k": max(top_k, 8),
                "document_ids": document_ids,
            },
        )

        second_verdict = self._verify_retrieval_result(question, second_pass, threshold=0.7)
        if second_verdict["ok"]:
            return {
                "ok": True,
                "stage": "second_pass",
                "relaxed_question": relaxed_question,
                "verdict": second_verdict,
                "retrieval_result": second_pass,
            }

        return {
            "ok": False,
            "stage": "failed",
            "relaxed_question": relaxed_question,
            "verdict": second_verdict,
            "retrieval_result": second_pass,
        }

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------

    def _general_knowledge_answer(self, question: str) -> Dict[str, Any]:
        prompt = f"""
Answer the user's question using general knowledge only.
Do not claim to have found supporting document context.
Be honest about uncertainty.

Question:
{question}
"""
        answer = self.llm.generate(prompt)
        return {
            "answer": answer,
            "citations": [],
            "fallback_notice": "未找到相关上下文，已基于通用知识回答。",
            "used_general_knowledge": True,
        }

    def _format_final_answer(self, question: str, tool_name: str, tool_result: Dict[str, Any]) -> str:
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
- If fallback_notice exists, surface it clearly.
- If answer exists, present it directly.
- If summary exists, present it directly.
- If comparison exists, present it directly.
- If roast exists, present it directly.
- If citations are present, preserve them in structure when possible.
"""
        return self.llm.generate(prompt)
    
    
    def _is_roast_request(self, question: str) -> bool:

        q = question.lower()

        roast_keywords = [
            "roast",
            "roast me",
            "mock me",
            "make fun",
            "judge me",
            "吐槽",
            "评价我"
        ]

        return any(k in q for k in roast_keywords)

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------

    def run(
        self,
        question: str,
        method: str = "hybrid",
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        routing_prompt = self._build_tool_prompt(
            question=question,
            method=method,
            top_k=top_k,
            document_ids=document_ids,
        )

        routing_response = self.llm.generate(routing_prompt)
        decision = self._extract_json(routing_response)

        if not decision:
            tool_name = "answer_tool"
            arguments = {
                "question": question,
                "method": method,
                "top_k": top_k,
                "document_ids": document_ids,
            }
        else:
            tool_name = decision.get("tool", "answer_tool")
            arguments = self._inject_missing_parameters(
                tool_name=tool_name,
                arguments=decision.get("arguments", {}),
                question=question,
                method=method,
                top_k=top_k,
                document_ids=document_ids,
            )

        verifier_report = None
        
        if self._is_roast_request(question):
            return {
                "tool_used": "roast_redirect",
                "tool_arguments": {},
                "tool_result": {
                    "answer": (
                        "想要完整的 Roast 分析？\n\n"
                        "请点击 Roast Page 按钮生成你的专属吐槽报告。"
                    ),
                    "citations": [],
                },
                "ui_action": "open_roast_page",
                "final_answer": (
                    "想要完整的 Roast 分析？\n\n"
                    "请点击 Roast Page 按钮生成完整分析报告。"
                ),
            }

        # Hard gate before roast / summary / compare
        if tool_name in self.CONTEXT_REQUIRED_TOOLS:
            probe_question = arguments.get("query") or arguments.get("question") or question

            if tool_name == "document_summary_tool":
                scope_document_ids = [arguments["document_id"]] if arguments.get("document_id") else (document_ids or [])
            else:
                scope_document_ids = arguments.get("document_ids") or document_ids

            verifier_report = self._probe_context(
                question=probe_question,
                method=arguments.get("method", method),
                top_k=arguments.get("top_k", top_k),
                document_ids=scope_document_ids,
            )

            if not verifier_report["ok"]:
                tool_name = "answer_tool"
                arguments = {
                    "question": question,
                    "method": method,
                    "top_k": top_k,
                    "document_ids": document_ids,
                }

                # Strict reading of your requirement:
                # we trigger answer_tool path, but return explicit generic fallback payload
                # instead of letting empty-context RAG hallucinate
                tool_result = self._general_knowledge_answer(question)
                tool_result["retrieval_verifier"] = verifier_report
                final_answer = self._format_final_answer(question, tool_name, tool_result)

                return {
                    "tool_used": tool_name,
                    "tool_arguments": arguments,
                    "tool_result": tool_result,
                    "final_answer": final_answer,
                }

        tool_result = self.executor.execute(tool_name, arguments)

        if verifier_report is not None:
            tool_result["retrieval_verifier"] = verifier_report

        final_answer = self._format_final_answer(
            question=question,
            tool_name=tool_name,
            tool_result=tool_result,
        )

        return {
            "tool_used": tool_name,
            "tool_arguments": arguments,
            "tool_result": tool_result,
            "final_answer": final_answer,
        }
        
    