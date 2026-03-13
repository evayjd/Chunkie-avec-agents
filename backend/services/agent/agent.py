import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.services.llm.ollama_client import OllamaClient


@dataclass
class TraceStep:
    thought: str
    action: str
    observation: str


@dataclass
class WorkflowState:
    question: str
    method: str = "hybrid"
    top_k: int = 5
    document_ids: Optional[List[str]] = None
    target_id: Optional[str] = None
    style_preference: Optional[str] = None

    selected_tool: str = "answer_tool"
    raw_arguments: Dict[str, Any] = field(default_factory=dict)
    final_arguments: Dict[str, Any] = field(default_factory=dict)

    retrieval_probe: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    final_answer: Optional[str] = None

    status: str = "INIT"
    trace: List[Dict[str, str]] = field(default_factory=list)


class Agent:
    """
    Workflow-based agent with 3 explicit stages:

    Stage 1: Retrieval & Audit
    Stage 2: Data Contract & Parameter Injection
    Stage 3: Execution Loop
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

    # ---------------------------------------------------------
    # Trace helper
    # ---------------------------------------------------------

    def _log(self, state: WorkflowState, thought: str, action: str, observation: str) -> None:
        state.trace.append({
            "thought": thought,
            "action": action,
            "observation": observation,
        })

    # ---------------------------------------------------------
    # Planner
    # ---------------------------------------------------------

    def _build_planner_prompt(self, state: WorkflowState) -> str:
        tool_specs = self.registry.get_tool_specs()
        tools_text = json.dumps(tool_specs, ensure_ascii=False, indent=2)

        return f"""
You are a workflow planner for a retrieval-grounded agent.

You must return ONLY valid JSON.

Available tools:
{tools_text}

User question:
{state.question}

Context:
- method = {state.method}
- top_k = {state.top_k}
- document_ids = {state.document_ids}
- target_id = {state.target_id}
- style_preference = {state.style_preference}

Hard rules:
1. roast_tool is only for explicit roast / persona teardown / humorous critique requests.
2. document_summary_tool requires a concrete target_id.
3. document_compare_tool requires at least 2 document_ids.
4. For roast_tool, target_id and style_preference must be non-empty.
5. If parameters cannot be satisfied, choose answer_tool.
6. Never return empty required fields.

Return JSON only:
{{
  "thought": "brief reasoning",
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

    def _plan(self, state: WorkflowState) -> None:
        prompt = self._build_planner_prompt(state)
        response = self.llm.generate(prompt)
        decision = self._extract_json(response)

        if not decision:
            state.selected_tool = "answer_tool"
            state.raw_arguments = {"question": state.question}
            self._log(
                state,
                "Planner output was invalid JSON; fallback to safe QA path.",
                "plan_tool -> answer_tool",
                "Invalid planner output; selected answer_tool.",
            )
            return

        state.selected_tool = decision.get("tool", "answer_tool")
        state.raw_arguments = decision.get("arguments", {}) or {}

        self._log(
            state,
            decision.get("thought", "Select the best tool for the request."),
            f"plan_tool -> {state.selected_tool}",
            f"Planner selected {state.selected_tool}.",
        )

    # ---------------------------------------------------------
    # Parameter inference
    # ---------------------------------------------------------

    def _extract_uuid_candidates(self, text: str) -> List[str]:
        pattern = r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
        return re.findall(pattern, text or "")

    def _infer_target_id(self, state: WorkflowState, args: Dict[str, Any]) -> Optional[str]:
        if isinstance(args.get("target_id"), str) and args["target_id"].strip():
            return args["target_id"].strip()

        if isinstance(state.target_id, str) and state.target_id.strip():
            return state.target_id.strip()

        mentioned = self._extract_uuid_candidates(state.question)
        if mentioned:
            return mentioned[0]

        if state.document_ids and len(state.document_ids) == 1:
            return state.document_ids[0]

        return None

    # ---------------------------------------------------------
    # Stage 2: contract alignment
    # ---------------------------------------------------------

    def _inject_and_validate_contract(self, state: WorkflowState) -> bool:
        tool_name = state.selected_tool
        args = dict(state.raw_arguments or {})

        # common defaults
        args.setdefault("method", state.method)

        if tool_name == "rag_search_tool":
            args.setdefault("question", state.question)
            args.setdefault("top_k", state.top_k)
            args.setdefault("document_ids", state.document_ids)

        elif tool_name == "answer_tool":
            args.setdefault("question", state.question)
            args.setdefault("top_k", state.top_k)
            args.setdefault("document_ids", state.document_ids)

        elif tool_name == "document_summary_tool":
            target_id = self._infer_target_id(state, args)
            if not target_id:
                self._log(
                    state,
                    "Summary requires a concrete target_id.",
                    "inject_contract(document_summary_tool)",
                    "Contract failed: target_id is missing.",
                )
                return False

            args["target_id"] = target_id
            args.setdefault("top_k", max(state.top_k, 8))
            args.setdefault("style_preference", state.style_preference or "concise_brief")

        elif tool_name == "document_compare_tool":
            doc_ids = args.get("document_ids") or state.document_ids or []
            if not isinstance(doc_ids, list) or len(doc_ids) < 2:
                self._log(
                    state,
                    "Compare requires at least two document_ids.",
                    "inject_contract(document_compare_tool)",
                    "Contract failed: document_ids < 2.",
                )
                return False

            args["document_ids"] = doc_ids
            args.setdefault("top_k", max(state.top_k, 6))
            args.setdefault("style_preference", state.style_preference or "contrastive_structured")

        elif tool_name == "roast_tool":
            target_id = self._infer_target_id(state, args)
            style_preference = args.get("style_preference") or state.style_preference or "sharp_witty"

            if not target_id:
                self._log(
                    state,
                    "Roast requires a concrete target_id.",
                    "inject_contract(roast_tool)",
                    "Contract failed: target_id is missing.",
                )
                return False

            args.setdefault("query", state.question)
            args["target_id"] = target_id
            args["style_preference"] = style_preference
            args.setdefault("top_k", max(state.top_k, 6))
            args.setdefault("document_ids", state.document_ids or [target_id])

        else:
            args = {
                "question": state.question,
                "method": state.method,
                "top_k": state.top_k,
                "document_ids": state.document_ids,
            }
            state.selected_tool = "answer_tool"

        state.final_arguments = args

        self._log(
            state,
            "Normalize tool arguments and enforce required contract fields.",
            f"inject_contract({state.selected_tool})",
            f"Contract passed with arguments: {json.dumps(args, ensure_ascii=False)}",
        )
        return True

    # ---------------------------------------------------------
    # Stage 1: retrieval audit
    # ---------------------------------------------------------

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]+", (text or "").lower())
        return [t for t in tokens if len(t) >= 2]

    def _relax_query(self, question: str) -> str:
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "to", "of", "for", "and",
            "or", "in", "on", "with", "about", "what", "which", "who", "why", "how",
            "请", "帮我", "一下", "关于", "这个", "那个", "什么", "怎么", "如何",
        }
        tokens = self._tokenize(question)
        relaxed = [t for t in tokens if t not in stopwords]
        return " ".join(relaxed[:10]).strip() or question.strip()

    def _verify_retrieval_result(
        self,
        question: str,
        retrieval_result: Dict[str, Any],
        threshold: float = 0.7,
    ) -> Dict[str, Any]:
        chunks = retrieval_result.get("chunks", []) if isinstance(retrieval_result, dict) else []

        if not chunks:
            return {
                "ok": False,
                "score": 0.0,
                "reason": "empty",
                "retrieval_count": 0,
            }

        q_tokens = set(self._tokenize(question))
        if not q_tokens:
            return {
                "ok": False,
                "score": 0.0,
                "reason": "empty_question_tokens",
                "retrieval_count": len(chunks),
            }

        scores = []
        for c in chunks:
            c_tokens = set(self._tokenize(c.get("content", "")))
            if not c_tokens:
                scores.append(0.0)
                continue

            overlap = len(q_tokens & c_tokens)
            recall = overlap / max(1, len(q_tokens))
            precision = overlap / max(1, len(c_tokens))
            score = (0.7 * recall) + (0.3 * precision)
            scores.append(score)

        best_score = max(scores) if scores else 0.0
        avg_score = sum(scores) / len(scores) if scores else 0.0
        final_score = round((0.75 * best_score) + (0.25 * avg_score), 3)

        return {
            "ok": final_score >= threshold,
            "score": final_score,
            "reason": "passed" if final_score >= threshold else "below_threshold",
            "retrieval_count": len(chunks),
        }

    def _probe_context(self, state: WorkflowState) -> Dict[str, Any]:
        probe_query = state.final_arguments.get("query") or state.final_arguments.get("question") or state.question
        probe_document_ids = state.final_arguments.get("document_ids") or state.document_ids
        probe_top_k = state.final_arguments.get("top_k", max(state.top_k, 6))
        probe_method = state.final_arguments.get("method", state.method)

        first_pass = self.executor.execute("rag_search_tool", {
            "question": probe_query,
            "method": probe_method,
            "top_k": probe_top_k,
            "document_ids": probe_document_ids,
        })
        first_verdict = self._verify_retrieval_result(probe_query, first_pass, threshold=0.7)

        if first_verdict["ok"]:
            self._log(
                state,
                "Audit grounded context before executing a context-dependent tool.",
                "rag_search_tool(first_pass)",
                f"Audit passed on first pass with score={first_verdict['score']}.",
            )
            return {
                "ok": True,
                "stage": "first_pass",
                "verdict": first_verdict,
                "retrieval_result": first_pass,
            }

        relaxed_query = self._relax_query(probe_query)
        second_pass = self.executor.execute("rag_search_tool", {
            "question": relaxed_query,
            "method": probe_method,
            "top_k": max(probe_top_k, 8),
            "document_ids": probe_document_ids,
        })
        second_verdict = self._verify_retrieval_result(probe_query, second_pass, threshold=0.7)

        if second_verdict["ok"]:
            self._log(
                state,
                "First retrieval audit failed; retry with relaxed query.",
                "rag_search_tool(second_pass)",
                f"Audit passed on retry with score={second_verdict['score']}; relaxed_query={relaxed_query}",
            )
            return {
                "ok": True,
                "stage": "second_pass",
                "relaxed_query": relaxed_query,
                "verdict": second_verdict,
                "retrieval_result": second_pass,
            }

        self._log(
            state,
            "Both retrieval audits failed; must not continue into roast/summary/compare.",
            "rag_search_tool(second_pass)",
            f"Audit failed after retry; score={second_verdict['score']}; relaxed_query={relaxed_query}",
        )
        return {
            "ok": False,
            "stage": "failed",
            "relaxed_query": relaxed_query,
            "verdict": second_verdict,
            "retrieval_result": second_pass,
        }

    # ---------------------------------------------------------
    # Stage 3: execution + output contract
    # ---------------------------------------------------------

    def _inject_audited_evidence(self, state: WorkflowState) -> None:
        if not state.retrieval_probe or not state.retrieval_probe.get("ok"):
            return

        retrieval_result = state.retrieval_probe.get("retrieval_result", {})
        chunks = retrieval_result.get("chunks", [])

        if state.selected_tool in {"roast_tool", "document_summary_tool"}:
            state.final_arguments["evidence_chunks"] = chunks

    def _validate_tool_output(self, tool_name: str, tool_result: Dict[str, Any]) -> bool:
        if tool_name == "roast_tool":
            return bool(tool_result.get("roast_text"))
        if tool_name == "document_summary_tool":
            return bool(tool_result.get("summary"))
        if tool_name == "document_compare_tool":
            return bool(tool_result.get("comparison"))
        if tool_name == "answer_tool":
            return bool(tool_result.get("answer"))
        if tool_name == "rag_search_tool":
            return isinstance(tool_result.get("citations"), list)
        return True

    def _format_final_answer(self, state: WorkflowState) -> str:
        prompt = f"""
You are a helpful assistant.

User question:
{state.question}

Tool used:
{state.selected_tool}

Tool result:
{json.dumps(state.tool_result or {}, ensure_ascii=False, indent=2)}

Generate the final user-facing response.

Rules:
- If fallback_notice exists, surface it clearly.
- If answer exists, present it directly.
- If summary exists, present it directly.
- If comparison exists, present it directly.
- If roast_text exists, present it directly.
"""
        return self.llm.generate(prompt)

    def _fallback_with_insufficient_context(self, state: WorkflowState) -> None:
        fallback_notice = (
            "未检索到足够可靠的上下文，已中断 Roast/Summary/Compare 流程，并回退到 answer_tool。"
        )

        state.selected_tool = "answer_tool"
        state.final_arguments = {
            "question": state.question,
            "method": state.method,
            "top_k": state.top_k,
            "document_ids": state.document_ids,
            "use_general_knowledge": True,
            "fallback_notice": fallback_notice,
        }

        self._log(
            state,
            "Context is insufficient; switch to the safe fallback path.",
            "answer_tool(use_general_knowledge=True)",
            "Fallback prepared due to retrieval audit failure.",
        )

        state.tool_result = self.executor.execute(state.selected_tool, state.final_arguments)
        state.final_answer = self._format_final_answer(state)
        state.status = "DONE"

    # ---------------------------------------------------------
    # Main workflow
    # ---------------------------------------------------------

    def run(
        self,
        question: str,
        method: str = "hybrid",
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        target_id: Optional[str] = None,
        style_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        state = WorkflowState(
            question=question,
            method=method,
            top_k=top_k,
            document_ids=document_ids,
            target_id=target_id,
            style_preference=style_preference,
        )

        # round 1: planning
        self._plan(state)

        # round 2: contract alignment
        contract_ok = self._inject_and_validate_contract(state)
        if not contract_ok:
            self._fallback_with_insufficient_context(state)
            return {
                "workflow_status": state.status,
                "tool_used": state.selected_tool,
                "tool_arguments": state.final_arguments,
                "tool_result": state.tool_result,
                "final_answer": state.final_answer,
                "trace": state.trace,
            }

        # round 3: retrieval audit for context-dependent tools
        if state.selected_tool in self.CONTEXT_REQUIRED_TOOLS:
            state.retrieval_probe = self._probe_context(state)
            if not state.retrieval_probe["ok"]:
                self._fallback_with_insufficient_context(state)
                # 修复 Bug 2：executor.execute 可能返回 None，先做类型守卫再赋值
                if isinstance(state.tool_result, dict):
                    state.tool_result["retrieval_verifier"] = state.retrieval_probe
                return {
                    "workflow_status": state.status,
                    "tool_used": state.selected_tool,
                    "tool_arguments": state.final_arguments,
                    "tool_result": state.tool_result,
                    "final_answer": state.final_answer,
                    "trace": state.trace,
                }

            self._inject_audited_evidence(state)

        # round 4: execute target tool
        self._log(
            state,
            "Audit and contract checks passed; execute the selected tool.",
            f"execute({state.selected_tool})",
            "Tool execution started.",
        )

        state.tool_result = self.executor.execute(state.selected_tool, state.final_arguments)

        if state.retrieval_probe is not None and isinstance(state.tool_result, dict):
            state.tool_result["retrieval_verifier"] = state.retrieval_probe

        output_ok = self._validate_tool_output(state.selected_tool, state.tool_result)
        if not output_ok:
            self._log(
                state,
                "Tool output failed output contract validation.",
                f"validate_output({state.selected_tool})",
                "Output contract failed; fallback to answer_tool.",
            )
            self._fallback_with_insufficient_context(state)
            return {
                "workflow_status": state.status,
                "tool_used": state.selected_tool,
                "tool_arguments": state.final_arguments,
                "tool_result": state.tool_result,
                "final_answer": state.final_answer,
                "trace": state.trace,
            }

        self._log(
            state,
            "Tool output satisfies output contract.",
            f"validate_output({state.selected_tool})",
            "Output contract passed.",
        )

        state.final_answer = self._format_final_answer(state)
        state.status = "DONE"

        return {
            "workflow_status": state.status,
            "tool_used": state.selected_tool,
            "tool_arguments": state.final_arguments,
            "tool_result": state.tool_result,
            "final_answer": state.final_answer,
            "trace": state.trace,
        }