"""
Chunkie RAG Benchmark Suite
============================
评估维度：
  - Retrieval:  Precision@K, Recall@K, MRR, NDCG, Hit-Rate
  - Generation: Faithfulness, Answer Relevance, Context Recall (LLM-as-judge)
  - Chunking:   Avg chunk length, Non-empty ratio, Oversized chunk ratio
  - Agent:      Tool selection accuracy, Workflow completion rate
  - End-to-end: Answer Correctness (exact + semantic)

使用方式：
  python -m backend.evaluation.benchmark              # 全量评估
  python -m backend.evaluation.benchmark --suite retrieval  # 只跑检索评估
  python -m backend.evaluation.benchmark --method hybrid    # 对比指定检索方式
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import time
from dataclasses import dataclass, field, asdict
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Optional imports – graceful degradation if DB / models not available
# ---------------------------------------------------------------------------
try:
    from sqlalchemy.orm import Session
    from backend.core.database import SessionLocal
    from backend.services.retrieval.retriever_factory import get_retriever
    from backend.services.generation.answer_generator import AnswerGenerator
    from backend.services.ingestion.chunking.text_chunker import TextChunker
    from backend.services.llm.ollama_client import OllamaClient
    _BACKEND_AVAILABLE = True
except ImportError:
    _BACKEND_AVAILABLE = False


# ===========================================================================
# Dataset
# ===========================================================================

@dataclass
class QAItem:
    """单条评估样本"""
    id: str
    question: str
    ground_truth_answer: str
    relevant_chunk_ids: List[str]         # 相关 chunk id 列表（可为空）
    relevant_snippets: List[str]          # 相关文本片段（用于软匹配）
    document_ids: Optional[List[str]] = None
    expected_tool: Optional[str] = None  # agent 评估用
    category: str = "general"


BENCHMARK_DATASET: List[QAItem] = [
    # ── 事实性问答 ──────────────────────────────────────────────────────────
    QAItem(
        id="q001",
        question="What is RAG (Retrieval-Augmented Generation)?",
        ground_truth_answer=(
            "RAG is a technique that combines a retrieval system with a language model. "
            "It retrieves relevant documents from a knowledge base and uses them as context "
            "to generate accurate, grounded answers."
        ),
        relevant_chunk_ids=[],
        relevant_snippets=[
            "retrieval-augmented generation",
            "combines retrieval with language model",
            "knowledge base",
        ],
        category="factual",
    ),
    QAItem(
        id="q002",
        question="What is the difference between dense and sparse retrieval?",
        ground_truth_answer=(
            "Dense retrieval uses neural embeddings (vectors) to find semantically similar documents. "
            "Sparse retrieval uses keyword matching (e.g., BM25/TF-IDF). "
            "Hybrid approaches combine both for better coverage."
        ),
        relevant_chunk_ids=[],
        relevant_snippets=[
            "dense retrieval",
            "sparse retrieval",
            "BM25",
            "embedding",
            "keyword",
        ],
        category="factual",
    ),
    QAItem(
        id="q003",
        question="What is Reciprocal Rank Fusion (RRF)?",
        ground_truth_answer=(
            "RRF is a rank fusion algorithm that combines results from multiple ranked lists. "
            "Each document gets a score of 1/(k + rank), where k is a constant (often 60). "
            "Scores are summed across lists to produce the final ranking."
        ),
        relevant_chunk_ids=[],
        relevant_snippets=[
            "reciprocal rank fusion",
            "rank fusion",
            "1/(k + rank)",
            "ranked lists",
        ],
        category="factual",
    ),
    # ── 推理性问答 ──────────────────────────────────────────────────────────
    QAItem(
        id="q004",
        question="Why does chunk overlap help RAG performance?",
        ground_truth_answer=(
            "Chunk overlap ensures that sentences near chunk boundaries appear in multiple chunks, "
            "preventing context loss. This helps when a relevant answer spans the boundary between "
            "two adjacent chunks."
        ),
        relevant_chunk_ids=[],
        relevant_snippets=[
            "chunk overlap",
            "context continuity",
            "boundary",
            "adjacent chunks",
        ],
        category="reasoning",
    ),
    QAItem(
        id="q005",
        question="When should a cross-encoder reranker be used instead of a bi-encoder?",
        ground_truth_answer=(
            "A cross-encoder attends to both the query and document jointly, giving better accuracy "
            "but higher latency. It should be used for reranking a small candidate set (e.g., top-20) "
            "retrieved by a fast bi-encoder, not for first-stage retrieval over large corpora."
        ),
        relevant_chunk_ids=[],
        relevant_snippets=[
            "cross-encoder",
            "bi-encoder",
            "reranking",
            "latency",
            "candidate set",
        ],
        category="reasoning",
    ),
    # ── 摘要 / 对比 ─────────────────────────────────────────────────────────
    QAItem(
        id="q006",
        question="Compare vector search and keyword search for document retrieval.",
        ground_truth_answer=(
            "Vector search captures semantic similarity even when exact words differ, but may miss "
            "specific terms. Keyword search is exact but fails on paraphrasing. Hybrid search "
            "combining both typically achieves the best recall and precision."
        ),
        relevant_chunk_ids=[],
        relevant_snippets=[
            "vector search",
            "keyword search",
            "semantic similarity",
            "exact match",
            "hybrid",
        ],
        category="comparison",
    ),
    # ── Agent 工具选择 ───────────────────────────────────────────────────────
    QAItem(
        id="q007",
        question="Summarize the document uploaded by the user.",
        ground_truth_answer="",
        relevant_chunk_ids=[],
        relevant_snippets=[],
        expected_tool="document_summary_tool",
        category="agent",
    ),
    QAItem(
        id="q008",
        question="Compare the two uploaded research papers.",
        ground_truth_answer="",
        relevant_chunk_ids=[],
        relevant_snippets=[],
        expected_tool="document_compare_tool",
        category="agent",
    ),
    QAItem(
        id="q009",
        question="Roast me based on my uploaded documents.",
        ground_truth_answer="",
        relevant_chunk_ids=[],
        relevant_snippets=[],
        expected_tool="roast_tool",
        category="agent",
    ),
    QAItem(
        id="q010",
        question="What are the key findings mentioned in the document?",
        ground_truth_answer="",
        relevant_chunk_ids=[],
        relevant_snippets=["key findings", "results", "conclusion"],
        expected_tool="answer_tool",
        category="agent",
    ),
    # ── 中文问答 ──────────────────────────────────────────────────────────
    QAItem(
        id="q011",
        question="什么是向量数据库？",
        ground_truth_answer=(
            "向量数据库是专门存储和检索高维向量的数据库系统。"
            "它支持近似最近邻（ANN）搜索，广泛用于语义搜索和推荐系统。"
            "常见的向量数据库包括 Pinecone、Weaviate、Qdrant 和 pgvector。"
        ),
        relevant_chunk_ids=[],
        relevant_snippets=["向量数据库", "高维向量", "近似最近邻", "语义搜索"],
        category="factual_zh",
    ),
    QAItem(
        id="q012",
        question="文本分块的常见策略有哪些？",
        ground_truth_answer=(
            "常见的分块策略包括：固定大小分块、按句子分块、按段落分块、"
            "语义分块（利用嵌入模型识别主题边界）以及递归分块。"
            "每种策略都有各自的优缺点，选择取决于文档类型和下游任务。"
        ),
        relevant_chunk_ids=[],
        relevant_snippets=["文本分块", "分块策略", "固定大小", "语义分块"],
        category="factual_zh",
    ),
    # ── 边界情况 ──────────────────────────────────────────────────────────
    QAItem(
        id="q013",
        question="",  # 空问题 — 测试鲁棒性
        ground_truth_answer="",
        relevant_chunk_ids=[],
        relevant_snippets=[],
        category="edge_case",
    ),
    QAItem(
        id="q014",
        question="asdfghjklqwertyuiop",  # 无意义噪声查询
        ground_truth_answer="",
        relevant_chunk_ids=[],
        relevant_snippets=[],
        category="edge_case",
    ),
]


# ===========================================================================
# Metrics helpers
# ===========================================================================

def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]+", text.lower())


def token_f1(pred: str, ref: str) -> float:
    """Token-level F1 between prediction and reference."""
    pred_tokens = _tokenize(pred)
    ref_tokens = _tokenize(ref)
    if not pred_tokens or not ref_tokens:
        return 0.0
    common = set(pred_tokens) & set(ref_tokens)
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def exact_match(pred: str, ref: str) -> float:
    return 1.0 if pred.strip().lower() == ref.strip().lower() else 0.0


def snippet_recall(retrieved_contents: List[str], snippets: List[str]) -> float:
    """Fraction of reference snippets found in retrieved chunks."""
    if not snippets:
        return 1.0
    combined = " ".join(retrieved_contents).lower()
    found = sum(1 for s in snippets if s.lower() in combined)
    return found / len(snippets)


def precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    if not relevant_ids:
        return 1.0
    top_k = retrieved_ids[:k]
    hits = sum(1 for r in top_k if r in relevant_ids)
    return hits / k


def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    if not relevant_ids:
        return 1.0
    top_k = retrieved_ids[:k]
    hits = sum(1 for r in top_k if r in relevant_ids)
    return hits / len(relevant_ids)


def hit_rate(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    if not relevant_ids:
        return 1.0
    return 1.0 if any(r in relevant_ids for r in retrieved_ids) else 0.0


def mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    if not relevant_ids:
        return 1.0
    for rank, rid in enumerate(retrieved_ids, start=1):
        if rid in relevant_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    if not relevant_ids:
        return 1.0
    rel_set = set(relevant_ids)
    dcg = sum(
        1.0 / math.log2(i + 2)
        for i, rid in enumerate(retrieved_ids[:k])
        if rid in rel_set
    )
    ideal = sum(1.0 / math.log2(i + 2) for i in range(min(len(rel_set), k)))
    return dcg / ideal if ideal > 0 else 0.0


# ===========================================================================
# Retrieval Evaluator
# ===========================================================================

@dataclass
class RetrievalResult:
    question_id: str
    method: str
    precision_at_5: float = 0.0
    recall_at_5: float = 0.0
    mrr: float = 0.0
    ndcg_at_5: float = 0.0
    hit_rate: float = 0.0
    snippet_recall: float = 0.0
    latency_ms: float = 0.0
    retrieved_count: int = 0


def evaluate_retrieval(
    db: "Session",
    dataset: List[QAItem],
    method: str = "hybrid",
    top_k: int = 5,
) -> Dict[str, Any]:
    retriever = get_retriever(method, db)
    results: List[RetrievalResult] = []

    for item in dataset:
        if item.category == "edge_case" or not item.question.strip():
            continue

        t0 = time.perf_counter()
        try:
            chunks = retriever.retrieve(
                question=item.question,
                document_ids=item.document_ids,
                top_k=top_k,
            )
        except Exception:
            chunks = []
        latency_ms = (time.perf_counter() - t0) * 1000

        retrieved_ids = [c.get("chunk_id", "") for c in chunks]
        retrieved_contents = [c.get("content", "") for c in chunks]

        r = RetrievalResult(
            question_id=item.id,
            method=method,
            precision_at_5=precision_at_k(retrieved_ids, item.relevant_chunk_ids, top_k),
            recall_at_5=recall_at_k(retrieved_ids, item.relevant_chunk_ids, top_k),
            mrr=mrr(retrieved_ids, item.relevant_chunk_ids),
            ndcg_at_5=ndcg_at_k(retrieved_ids, item.relevant_chunk_ids, top_k),
            hit_rate=hit_rate(retrieved_ids, item.relevant_chunk_ids),
            snippet_recall=snippet_recall(retrieved_contents, item.relevant_snippets),
            latency_ms=latency_ms,
            retrieved_count=len(chunks),
        )
        results.append(r)

    if not results:
        return {"method": method, "n": 0, "message": "No evaluable items."}

    def _avg(attr: str) -> float:
        vals = [getattr(r, attr) for r in results]
        return round(mean(vals), 4) if vals else 0.0

    def _std(attr: str) -> float:
        vals = [getattr(r, attr) for r in results]
        return round(stdev(vals), 4) if len(vals) > 1 else 0.0

    return {
        "method": method,
        "n": len(results),
        "precision_at_5": _avg("precision_at_5"),
        "recall_at_5": _avg("recall_at_5"),
        "mrr": _avg("mrr"),
        "ndcg_at_5": _avg("ndcg_at_5"),
        "hit_rate": _avg("hit_rate"),
        "snippet_recall": _avg("snippet_recall"),
        "avg_latency_ms": _avg("latency_ms"),
        "std_latency_ms": _std("latency_ms"),
        "per_question": [asdict(r) for r in results],
    }


# ===========================================================================
# Generation Evaluator (LLM-as-judge)
# ===========================================================================

_FAITHFULNESS_PROMPT = """\
You are an evaluation judge. Given a CONTEXT and an ANSWER, rate how faithful the answer is
to the context on a scale of 0 to 1 (1 = fully grounded, 0 = hallucinated).
Reply with ONLY a JSON object: {{"score": <float>}}

CONTEXT:
{context}

ANSWER:
{answer}
"""

_RELEVANCE_PROMPT = """\
You are an evaluation judge. Given a QUESTION and an ANSWER, rate how relevant the answer is
to the question on a scale of 0 to 1 (1 = perfectly relevant, 0 = completely irrelevant).
Reply with ONLY a JSON object: {{"score": <float>}}

QUESTION:
{question}

ANSWER:
{answer}
"""


@dataclass
class GenerationResult:
    question_id: str
    faithfulness: float = 0.0
    answer_relevance: float = 0.0
    token_f1: float = 0.0
    exact_match: float = 0.0
    latency_ms: float = 0.0


def _llm_score(llm: "OllamaClient", prompt: str) -> float:
    try:
        raw = llm.generate(prompt)
        match = re.search(r'"score"\s*:\s*([0-9.]+)', raw)
        if match:
            return min(1.0, max(0.0, float(match.group(1))))
    except Exception:
        pass
    return 0.0


def evaluate_generation(
    db: "Session",
    dataset: List[QAItem],
    method: str = "hybrid",
    top_k: int = 5,
) -> Dict[str, Any]:
    retriever = get_retriever(method, db)
    generator = AnswerGenerator()
    llm = OllamaClient()
    results: List[GenerationResult] = []

    for item in dataset:
        if not item.question.strip() or not item.ground_truth_answer.strip():
            continue

        try:
            chunks = retriever.retrieve(
                question=item.question,
                document_ids=item.document_ids,
                top_k=top_k,
            )
        except Exception:
            chunks = []

        context_str = "\n".join(c.get("content", "") for c in chunks)

        t0 = time.perf_counter()
        try:
            answer = generator.generate(item.question, chunks)
        except Exception:
            answer = ""
        latency_ms = (time.perf_counter() - t0) * 1000

        faithfulness = _llm_score(
            llm,
            _FAITHFULNESS_PROMPT.format(context=context_str[:3000], answer=answer)
        )
        relevance = _llm_score(
            llm,
            _RELEVANCE_PROMPT.format(question=item.question, answer=answer)
        )
        tf1 = token_f1(answer, item.ground_truth_answer)
        em = exact_match(answer, item.ground_truth_answer)

        results.append(GenerationResult(
            question_id=item.id,
            faithfulness=faithfulness,
            answer_relevance=relevance,
            token_f1=tf1,
            exact_match=em,
            latency_ms=latency_ms,
        ))

    if not results:
        return {"n": 0, "message": "No evaluable items."}

    def _avg(attr: str) -> float:
        vals = [getattr(r, attr) for r in results]
        return round(mean(vals), 4) if vals else 0.0

    return {
        "method": method,
        "n": len(results),
        "faithfulness": _avg("faithfulness"),
        "answer_relevance": _avg("answer_relevance"),
        "token_f1": _avg("token_f1"),
        "exact_match": _avg("exact_match"),
        "avg_latency_ms": _avg("latency_ms"),
        "per_question": [asdict(r) for r in results],
    }


# ===========================================================================
# Chunking Evaluator (offline – no DB required)
# ===========================================================================

def evaluate_chunking(
    sample_texts: Optional[List[str]] = None,
    chunk_size: int = 800,
    overlap: int = 120,
) -> Dict[str, Any]:
    """
    对给定文本执行 chunking 并统计质量指标。
    如果未传入 sample_texts，则使用内建样本。
    """
    chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)

    if sample_texts is None:
        sample_texts = [
            " ".join(["This is sentence number {}.".format(i)] * 3)
            for i in range(1, 30)
        ]

    all_chunks = []
    for text in sample_texts:
        doc = {
            "pages": [{"page_num": 1, "content": text, "section": None}],
            "text": text,
        }
        chunks = chunker.chunk(doc)
        all_chunks.extend(chunks)

    if not all_chunks:
        return {"error": "No chunks produced."}

    lengths = [len(c["content"]) for c in all_chunks]
    total = len(all_chunks)
    oversized = sum(1 for l in lengths if l > chunk_size * 1.2)
    undersized = sum(1 for l in lengths if l < chunker.MIN_CHUNK_LEN)
    empty = sum(1 for c in all_chunks if not c["content"].strip())

    return {
        "total_chunks": total,
        "avg_length": round(mean(lengths), 1),
        "std_length": round(stdev(lengths), 1) if total > 1 else 0.0,
        "min_length": min(lengths),
        "max_length": max(lengths),
        "oversized_ratio": round(oversized / total, 4),
        "undersized_ratio": round(undersized / total, 4),
        "empty_ratio": round(empty / total, 4),
        "config": {"chunk_size": chunk_size, "overlap": overlap},
    }


# ===========================================================================
# Agent Tool Selection Evaluator
# ===========================================================================

def evaluate_agent_tool_selection(
    db: "Session",
    dataset: List[QAItem],
) -> Dict[str, Any]:
    """
    评估 Agent 规划阶段的工具选择准确率。
    只评估 category=='agent' 且 expected_tool 非空的样本。
    """
    from backend.services.agent.tool_registry import ToolRegistry
    from backend.services.agent.agent_executor import AgentExecutor
    from backend.services.agent.agent import Agent

    registry = ToolRegistry(db)
    executor = AgentExecutor(db)
    agent = Agent(registry, executor)

    items = [i for i in dataset if i.category == "agent" and i.expected_tool]
    if not items:
        return {"n": 0, "message": "No agent evaluation items."}

    correct = 0
    details = []
    for item in items:
        try:
            result = agent.run(
                question=item.question,
                document_ids=item.document_ids or [],
            )
            selected = result.get("tool_used", "")
        except Exception as e:
            selected = f"error: {e}"

        is_correct = selected == item.expected_tool
        if is_correct:
            correct += 1
        details.append({
            "id": item.id,
            "question": item.question,
            "expected": item.expected_tool,
            "selected": selected,
            "correct": is_correct,
        })

    return {
        "n": len(items),
        "accuracy": round(correct / len(items), 4),
        "per_question": details,
    }


# ===========================================================================
# End-to-end Benchmark Runner
# ===========================================================================

@dataclass
class BenchmarkReport:
    timestamp: str
    retrieval: Dict[str, Any] = field(default_factory=dict)
    generation: Dict[str, Any] = field(default_factory=dict)
    chunking: Dict[str, Any] = field(default_factory=dict)
    agent: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = ["=" * 60, "  CHUNKIE BENCHMARK REPORT", "=" * 60]

        def _section(title: str, data: Dict[str, Any]) -> None:
            lines.append(f"\n[{title}]")
            if "error" in data or "message" in data:
                lines.append(f"  {data.get('error') or data.get('message')}")
                return
            skip = {"per_question", "method", "config"}
            for k, v in data.items():
                if k not in skip:
                    lines.append(f"  {k:<28} {v}")

        for method, res in self.retrieval.items():
            _section(f"RETRIEVAL / {method.upper()}", res)
        _section("GENERATION", self.generation)
        _section("CHUNKING", self.chunking)
        _section("AGENT TOOL SELECTION", self.agent)
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"[benchmark] Report saved to {path}")


def run_benchmark(
    suite: str = "all",
    methods: Optional[List[str]] = None,
    top_k: int = 5,
    output_path: str = "benchmark_report.json",
) -> BenchmarkReport:
    from datetime import datetime

    report = BenchmarkReport(timestamp=datetime.utcnow().isoformat())

    if not _BACKEND_AVAILABLE:
        print("[benchmark] Backend not available – running offline chunking suite only.")
        report.chunking = evaluate_chunking()
        print(report.summary())
        return report

    if methods is None:
        methods = ["vector", "hybrid", "rerank"]

    db: Session = SessionLocal()
    try:
        if suite in ("all", "retrieval"):
            for m in methods:
                print(f"[benchmark] Evaluating retrieval method: {m} …")
                report.retrieval[m] = evaluate_retrieval(db, BENCHMARK_DATASET, method=m, top_k=top_k)

        if suite in ("all", "generation"):
            print("[benchmark] Evaluating generation …")
            report.generation = evaluate_generation(
                db, BENCHMARK_DATASET, method=methods[0], top_k=top_k
            )

        if suite in ("all", "chunking"):
            print("[benchmark] Evaluating chunking …")
            report.chunking = evaluate_chunking()

        if suite in ("all", "agent"):
            print("[benchmark] Evaluating agent tool selection …")
            report.agent = evaluate_agent_tool_selection(db, BENCHMARK_DATASET)

    finally:
        db.close()

    print(report.summary())
    report.save(output_path)
    return report


# ===========================================================================
# CLI entry point
# ===========================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chunkie RAG Benchmark")
    parser.add_argument(
        "--suite",
        choices=["all", "retrieval", "generation", "chunking", "agent"],
        default="all",
        help="Which evaluation suite to run",
    )
    parser.add_argument(
        "--method",
        nargs="+",
        default=None,
        help="Retrieval methods to compare (vector hybrid rerank)",
    )
    parser.add_argument("--top_k", type=int, default=5)
    parser.add_argument("--output", default="benchmark_report.json")
    args = parser.parse_args()

    run_benchmark(
        suite=args.suite,
        methods=args.method,
        top_k=args.top_k,
        output_path=args.output,
    )
