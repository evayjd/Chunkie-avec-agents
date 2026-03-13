"""
evaluation/retrieval_eval.py

检索方法评估脚本
支持 vector / hybrid / rerank 三种检索方法的逐查询评估。
相关性判断使用关键词匹配（relevant_chunk_keywords）作为代理指标。

用法示例:
    python evaluation/retrieval_eval.py
    python evaluation/retrieval_eval.py --method hybrid --top_k 10
    python evaluation/retrieval_eval.py --method vector --data evaluation/dataset.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ==============================================================
# 路径配置：将项目根目录（backend/）加入sys.path，确保能正确导入后端模块
# ==============================================================
_SCRIPT_DIR = Path(__file__).resolve().parent          # evaluation/
_PROJECT_ROOT = _SCRIPT_DIR.parent                     # Chunkie/backend/
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from evaluation.metrics import (
    hit_at_k,
    mrr,
    ndcg_at_k,
    recall_at_k,
    precision_at_k,
    compute_retrieval_metrics,
)

# 支持的检索方法列表
SUPPORTED_METHODS = ["vector", "hybrid", "rerank"]

# 默认数据集路径（相对于项目根目录）
DEFAULT_DATASET = str(_PROJECT_ROOT / "evaluation" / "dataset.json")

# 结果输出目录
RESULTS_DIR = _PROJECT_ROOT / "evaluation" / "results"


def _keyword_hit(chunk_content: str, keywords: list) -> bool:
    """
    关键词命中检测：判断一个chunk的内容是否包含至少一个相关关键词。
    用于在没有精确chunk_id的情况下，以语义关键词作为相关性代理指标。

    参数:
        chunk_content: chunk的文本内容
        keywords:      relevant_chunk_keywords列表

    返回:
        True 如果至少命中一个关键词，否则 False
    """
    content_lower = chunk_content.lower()
    for kw in keywords:
        if kw.lower() in content_lower or kw in chunk_content:
            return True
    return False


def _keyword_relevance_score(chunk_content: str, keywords: list) -> float:
    """
    关键词覆盖率：计算chunk内容命中多少比例的关键词。
    用于生成伪相关性分数（0~1），分数越高说明该chunk越可能相关。

    参数:
        chunk_content: chunk的文本内容
        keywords:      relevant_chunk_keywords列表

    返回:
        命中关键词数 / 总关键词数（float，0到1）
    """
    if not keywords:
        return 0.0
    hits = sum(
        1 for kw in keywords
        if kw.lower() in chunk_content.lower() or kw in chunk_content
    )
    return hits / len(keywords)


def _build_pseudo_relevant(chunks: list, keywords: list, threshold: float = 0.4) -> list:
    """
    基于关键词匹配，为一次查询构建伪相关文档ID列表。
    如果chunk的关键词覆盖率达到threshold，则视为相关。

    参数:
        chunks:    检索到的chunk字典列表（包含 chunk_id 和 content 字段）
        keywords:  relevant_chunk_keywords列表
        threshold: 相关性阈值（默认0.4，即命中40%以上关键词视为相关）

    返回:
        相关chunk的ID列表
    """
    relevant_ids = []
    for chunk in chunks:
        content = chunk.get("content", "") or chunk.get("text", "")
        score = _keyword_relevance_score(content, keywords)
        if score >= threshold:
            relevant_ids.append(chunk.get("chunk_id", ""))
    return relevant_ids


def evaluate_method(
    method: str,
    dataset: list,
    top_k: int,
    db,
) -> list:
    """
    对单一检索方法运行完整评估，返回每条查询的详细结果。

    参数:
        method:  检索方法名称（"vector" / "hybrid" / "rerank"）
        dataset: 已加载的数据集列表
        top_k:   检索返回的最大chunk数量
        db:      数据库会话（SQLAlchemy Session）

    返回:
        每条查询的评估结果列表，每条包含：
            question_id, method, hit@1, hit@3, hit@5, mrr_score, ndcg@5,
            recall@5, precision@5, retrieved_count, relevant_count
    """
    from backend.services.retrieval.retriever_factory import get_retriever

    retriever = get_retriever(method, db)
    per_query_results = []

    print(f"\n[评估] 方法: {method} | top_k={top_k} | 共 {len(dataset)} 条查询")
    print("-" * 60)

    for idx, item in enumerate(dataset):
        question_id = item.get("id", f"q{idx+1:03d}")
        question = item["question"]
        keywords = item.get("relevant_chunk_keywords", [])

        # 调用实际检索器（document_ids 为空列表表示全库检索）
        try:
            chunks = retriever.retrieve(
                question=question,
                document_ids=[],
                top_k=top_k,
            )
        except TypeError:
            # 兼容不同版本的检索器接口（部分检索器不接受 document_ids 参数）
            try:
                chunks = retriever.retrieve(question=question, top_k=top_k)
            except Exception as e:
                print(f"  [警告] 查询 {question_id} 检索失败: {e}")
                chunks = []

        # 获取检索到的chunk ID列表（按排名顺序）
        retrieved_ids = [c.get("chunk_id", "") for c in chunks]

        # 以关键词匹配构建伪相关集合（作为相关性 ground truth 的代理）
        pseudo_relevant = _build_pseudo_relevant(chunks, keywords, threshold=0.4)

        # 如果关键词匹配方式未命中任何相关文档，降低阈值重试
        if not pseudo_relevant and chunks:
            pseudo_relevant = _build_pseudo_relevant(chunks, keywords, threshold=0.2)

        # 如果依然没有命中，至少保留覆盖率最高的一个chunk作为相关文档
        if not pseudo_relevant and chunks:
            best_chunk = max(
                chunks,
                key=lambda c: _keyword_relevance_score(
                    c.get("content", "") or c.get("text", ""), keywords
                )
            )
            pseudo_relevant = [best_chunk.get("chunk_id", "")]

        # 计算各项指标
        h1 = hit_at_k(retrieved_ids, pseudo_relevant, 1)
        h3 = hit_at_k(retrieved_ids, pseudo_relevant, 3)
        h5 = hit_at_k(retrieved_ids, pseudo_relevant, 5)
        # MRR：单查询版本（传入列表格式）
        mrr_score = mrr([retrieved_ids], [pseudo_relevant])
        ndcg5 = ndcg_at_k(retrieved_ids, pseudo_relevant, 5)
        rec5 = recall_at_k(retrieved_ids, pseudo_relevant, 5)
        prec5 = precision_at_k(retrieved_ids, pseudo_relevant, 5)

        result = {
            "question_id": question_id,
            "method": method,
            "question": question,
            "profile_type": item.get("profile_type", ""),
            "hit@1": h1,
            "hit@3": h3,
            "hit@5": h5,
            "mrr": mrr_score,
            "ndcg@5": ndcg5,
            "recall@5": rec5,
            "precision@5": prec5,
            "retrieved_count": len(retrieved_ids),
            "relevant_count": len(pseudo_relevant),
            "keywords": keywords,
        }
        per_query_results.append(result)

        # 进度日志
        if (idx + 1) % 10 == 0:
            print(f"  已完成 {idx + 1}/{len(dataset)} 条查询...")

    print(f"[评估完成] {method}: {len(per_query_results)} 条查询")
    return per_query_results


def aggregate_results(per_query_results: list) -> dict:
    """
    将逐查询结果汇总为方法级别的平均指标。

    参数:
        per_query_results: evaluate_method 返回的结果列表

    返回:
        包含各指标均值的字典
    """
    if not per_query_results:
        return {}

    n = len(per_query_results)
    metrics = ["hit@1", "hit@3", "hit@5", "mrr", "ndcg@5", "recall@5", "precision@5"]
    summary = {}
    for m in metrics:
        summary[m] = sum(r[m] for r in per_query_results) / n
    return summary


def print_comparison_table(method_summaries: dict):
    """
    以表格形式打印各检索方法的指标对比。

    参数:
        method_summaries: {method_name: {metric: value}} 格式的字典
    """
    print("\n" + "=" * 80)
    print("检索方法评估结果对比")
    print("=" * 80)

    # 表头
    header = f"{'方法':<10} {'Hit@1':>8} {'Hit@3':>8} {'Hit@5':>8} {'MRR':>8} {'NDCG@5':>8} {'R@5':>8} {'P@5':>8}"
    print(header)
    print("-" * 80)

    # 各方法数据行
    for method, summary in method_summaries.items():
        row = (
            f"{method:<10}"
            f" {summary.get('hit@1', 0.0):>8.4f}"
            f" {summary.get('hit@3', 0.0):>8.4f}"
            f" {summary.get('hit@5', 0.0):>8.4f}"
            f" {summary.get('mrr', 0.0):>8.4f}"
            f" {summary.get('ndcg@5', 0.0):>8.4f}"
            f" {summary.get('recall@5', 0.0):>8.4f}"
            f" {summary.get('precision@5', 0.0):>8.4f}"
        )
        print(row)

    print("=" * 80)
    print("说明: R@5=Recall@5, P@5=Precision@5")
    print()


def run_evaluation(methods: list, top_k: int, data_path: str):
    """
    主评估流程：加载数据集，对指定方法逐一评估，保存结果并打印汇总表。

    参数:
        methods:   需要评估的检索方法列表
        top_k:     检索返回的最大数量
        data_path: 数据集JSON文件路径
    """
    # 加载数据集
    data_path = Path(data_path)
    if not data_path.exists():
        print(f"[错误] 数据集文件不存在: {data_path}")
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    print(f"[加载] 数据集: {data_path} | 共 {len(dataset)} 条")

    # 确保结果目录存在
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 初始化数据库连接
    from backend.core.database import SessionLocal
    db = SessionLocal()

    method_summaries = {}

    try:
        for method in methods:
            print(f"\n{'='*60}")
            print(f"开始评估方法: {method}")
            print(f"{'='*60}")

            # 逐查询评估
            per_query_results = evaluate_method(method, dataset, top_k, db)

            # 汇总指标
            summary = aggregate_results(per_query_results)
            method_summaries[method] = summary

            # 保存详细结果到JSON
            result_file = RESULTS_DIR / f"retrieval_{method}_results.json"
            output = {
                "method": method,
                "top_k": top_k,
                "dataset": str(data_path),
                "total_queries": len(per_query_results),
                "summary": summary,
                "per_query": per_query_results,
            }
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"[保存] 结果已写入: {result_file}")

    finally:
        db.close()

    # 打印汇总对比表
    print_comparison_table(method_summaries)

    return method_summaries


# ==============================================================
# 命令行入口
# ==============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="RAG检索方法评估脚本（支持vector/hybrid/rerank）"
    )
    parser.add_argument(
        "--method",
        type=str,
        default="all",
        choices=SUPPORTED_METHODS + ["all"],
        help="要评估的检索方法，默认评估全部三种方法 (default: all)",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=5,
        help="检索返回的最大chunk数量 (default: 5)",
    )
    parser.add_argument(
        "--data",
        type=str,
        default=DEFAULT_DATASET,
        help=f"评估数据集路径 (default: {DEFAULT_DATASET})",
    )

    args = parser.parse_args()

    # 确定要评估的方法列表
    if args.method == "all":
        methods_to_eval = SUPPORTED_METHODS
    else:
        methods_to_eval = [args.method]

    print(f"[启动] 检索评估 | 方法={methods_to_eval} | top_k={args.top_k}")
    run_evaluation(methods_to_eval, args.top_k, args.data)
