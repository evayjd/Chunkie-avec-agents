"""
evaluation/benchmark.py

RAG系统综合基准测试脚本
整合检索评估（retrieval_eval）与生成评估（generation_eval），
输出各检索方法的全量指标对比，并保存带时间戳的结果文件。

额外包含 generate_dataset.py 风格的数据集生成能力：
  使用 OllamaClient 从指定 document_id 生成中文QA数据集。

用法示例:
    python evaluation/benchmark.py
    python evaluation/benchmark.py --method hybrid
    python evaluation/benchmark.py --method all --top_k 10 --skip_generation
    python evaluation/benchmark.py --generate_only --document_id <doc_id> --num_pairs 20
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ==============================================================
# 路径配置：将项目根目录加入 sys.path
# ==============================================================
_SCRIPT_DIR = Path(__file__).resolve().parent          # evaluation/
_PROJECT_ROOT = _SCRIPT_DIR.parent                     # Chunkie/backend/
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from evaluation.metrics import (
    compute_retrieval_metrics,
    compute_generation_metrics,
    rouge_l,
    token_f1,
    faithfulness_recall,
)
from evaluation.retrieval_eval import (
    evaluate_method as run_retrieval_eval,
    aggregate_results,
    SUPPORTED_METHODS,
    DEFAULT_DATASET,
    RESULTS_DIR,
)

# 默认评估参数
DEFAULT_TOP_K = 5
# 生成评估时调用的 API 地址
ASK_API_URL = "http://localhost:8000/ask"
ROAST_API_URL = "http://localhost:8000/roast"


# ==============================================================
# 生成评估（Generation Eval）
# ==============================================================

def run_generation_eval(dataset: list, top_k: int = 5) -> list:
    """
    对数据集中每条问题调用 /ask 或 /roast API，收集生成结果并计算生成指标。

    参数:
        dataset: 已加载的数据集列表
        top_k:   检索时使用的 top_k 参数

    返回:
        每条查询的生成评估结果列表，每条包含：
            question_id, pred, gold, rouge_l, token_f1, faithfulness_recall
    """
    import requests

    results = []
    print(f"\n[生成评估] 共 {len(dataset)} 条查询，调用 API...")

    for idx, item in enumerate(dataset):
        question_id = item.get("id", f"q{idx+1:03d}")
        question = item["question"]
        gold = item.get("ground_truth", "")
        expected_tool = item.get("expected_tool", "answer_tool")

        # 根据 expected_tool 选择调用的 API
        api_url = ROAST_API_URL if expected_tool == "roast_tool" else ASK_API_URL

        try:
            resp = requests.post(
                api_url,
                json={"question": question, "top_k": top_k},
                timeout=60,
            )
            data = resp.json()
            pred = data.get("answer", "") or data.get("roast", "") or ""
            chunks = [
                c.get("content", "") or c.get("text", "")
                for c in data.get("citations", [])
            ]
        except Exception as e:
            print(f"  [警告] 查询 {question_id} API调用失败: {e}")
            pred = ""
            chunks = []

        # 计算生成指标
        rl = rouge_l(pred, gold)
        tf1 = token_f1(pred, gold)
        faith = faithfulness_recall(pred, chunks)

        results.append({
            "question_id": question_id,
            "question": question,
            "pred": pred,
            "gold": gold,
            "rouge_l": rl,
            "token_f1": tf1,
            "faithfulness_recall": faith,
            "expected_tool": expected_tool,
            "chunks": chunks,
        })

        if (idx + 1) % 10 == 0:
            print(f"  已完成 {idx + 1}/{len(dataset)} 条...")

    return results


def aggregate_generation_results(gen_results: list) -> dict:
    """
    汇总生成评估结果为平均指标。

    参数:
        gen_results: run_generation_eval 返回的结果列表

    返回:
        包含 rouge_l、token_f1、faithfulness_recall 均值的字典
    """
    if not gen_results:
        return {}
    n = len(gen_results)
    return {
        "rouge_l": sum(r["rouge_l"] for r in gen_results) / n,
        "token_f1": sum(r["token_f1"] for r in gen_results) / n,
        "faithfulness_recall": sum(r["faithfulness_recall"] for r in gen_results) / n,
    }


# ==============================================================
# 生成评估结果保存
# ==============================================================

def save_benchmark_results(
    method: str,
    retrieval_summary: dict,
    generation_summary: dict,
    per_query_retrieval: list,
    per_query_generation: list,
    top_k: int,
    dataset_path: str,
) -> Path:
    """
    将单个方法的完整基准测试结果保存为带时间戳的JSON文件。

    参数:
        method:                检索方法名称
        retrieval_summary:     检索指标汇总
        generation_summary:    生成指标汇总
        per_query_retrieval:   逐查询检索结果
        per_query_generation:  逐查询生成结果
        top_k:                 检索参数
        dataset_path:          数据集路径

    返回:
        保存的文件路径
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = RESULTS_DIR / f"benchmark_{method}_{timestamp}.json"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "method": method,
        "timestamp": timestamp,
        "top_k": top_k,
        "dataset": str(dataset_path),
        "retrieval_summary": retrieval_summary,
        "generation_summary": generation_summary,
        "per_query_retrieval": per_query_retrieval,
        "per_query_generation": per_query_generation,
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[保存] 基准测试结果: {filename}")
    return filename


# ==============================================================
# Markdown 对比表格打印
# ==============================================================

def print_markdown_table(all_results: dict):
    """
    打印 Markdown 格式的方法对比表格（适合复制到文档或 README 中）。

    参数:
        all_results: {method: {"retrieval": {...}, "generation": {...}}} 格式的字典
    """
    print("\n" + "=" * 90)
    print("基准测试综合对比（Markdown格式）")
    print("=" * 90)

    # 表头
    header = (
        "| {:<8} | {:>7} | {:>7} | {:>7} | {:>7} | {:>8} | {:>8} |"
        .format("Method", "Hit@1", "Hit@3", "Hit@5", "MRR", "NDCG@5", "ROUGE-L")
    )
    separator = (
        "| {:-<8} | {:-<7} | {:-<7} | {:-<7} | {:-<7} | {:-<8} | {:-<8} |"
        .format("", "", "", "", "", "", "")
    )

    print(header)
    print(separator)

    for method, results in all_results.items():
        ret = results.get("retrieval", {})
        gen = results.get("generation", {})
        row = (
            "| {:<8} | {:>7.4f} | {:>7.4f} | {:>7.4f} | {:>7.4f} | {:>8.4f} | {:>8.4f} |"
            .format(
                method,
                ret.get("hit@1", 0.0),
                ret.get("hit@3", 0.0),
                ret.get("hit@5", 0.0),
                ret.get("mrr", 0.0),
                ret.get("ndcg@5", 0.0),
                gen.get("rouge_l", 0.0),
            )
        )
        print(row)

    print()

    # 附加生成指标表格
    print("| {:<8} | {:>10} | {:>15} |".format("Method", "Token-F1", "Faithfulness"))
    print("| {:-<8} | {:-<10} | {:-<15} |".format("", "", ""))
    for method, results in all_results.items():
        gen = results.get("generation", {})
        print(
            "| {:<8} | {:>10.4f} | {:>15.4f} |".format(
                method,
                gen.get("token_f1", 0.0),
                gen.get("faithfulness_recall", 0.0),
            )
        )
    print()


# ==============================================================
# 数据集生成（generate_dataset 能力）
# ==============================================================

def generate_dataset_from_document(
    document_id: str,
    num_pairs: int = 20,
    output_path: str = None,
) -> list:
    """
    使用 OllamaClient 从指定文档中自动生成中文QA数据集。
    生成格式与 dataset.json 保持一致，可直接追加使用。

    参数:
        document_id: 要生成QA对的文档ID（需要已存在于数据库中）
        num_pairs:   希望生成的QA对数量（默认20）
        output_path: 输出JSON文件路径（默认 evaluation/generated_dataset_{doc_id}.json）

    返回:
        生成的QA对列表
    """
    from backend.services.llm.ollama_client import OllamaClient
    from backend.core.database import SessionLocal
    from backend.db.repositories.chunk_repo import ChunkRepository

    print(f"\n[生成数据集] document_id={document_id}, num_pairs={num_pairs}")

    db = SessionLocal()
    try:
        # 从数据库获取文档的chunk内容作为上下文
        chunk_repo = ChunkRepository(db)
        chunks = chunk_repo.get_chunks_by_document(document_id)
        if not chunks:
            print(f"[警告] 文档 {document_id} 没有找到任何chunk，无法生成数据集")
            return []

        # 取前5个chunk作为上下文样本（避免超出LLM上下文窗口）
        context_chunks = chunks[:5]
        context_text = "\n\n".join(
            c.content for c in context_chunks if hasattr(c, "content")
        )

        print(f"  使用 {len(context_chunks)} 个chunk作为上下文（共 {len(chunks)} 个）")
    finally:
        db.close()

    # 构建提示词
    system_prompt = """你是一个专业的中文简历RAG评估数据集生成助手。
你的任务是根据给定的简历文本片段，生成用于RAG系统评估的中文问答对。
严格按照指定的JSON格式输出，不要添加任何额外说明。"""

    user_prompt = f"""请根据以下简历文本片段，生成 {num_pairs} 个中文QA评估对。

【简历文本片段】
{context_text}

【输出格式要求】
返回一个JSON数组，每个元素包含以下字段：
- "id": 字符串，格式如 "gen001"
- "profile_type": 简历类型（应届生/跳槽者/管理层/海归/转行者 中选一个）
- "question": 中文问题（针对简历内容的真实问题）
- "ground_truth": 中文标准答案（根据简历内容回答）
- "relevant_chunk_keywords": 3-5个中文关键词列表
- "expected_tool": "answer_tool" 或 "roast_tool"（90%用answer_tool，10%用roast_tool）
- "language": "zh"

问题类型需覆盖：事实提取、技能匹配、经历比较、矛盾发现、Roast触发。
只返回JSON数组，不要有任何其他文字。"""

    client = OllamaClient()
    print("  调用 OllamaClient 生成QA对...")

    try:
        raw_response = client.chat(system=system_prompt, user=user_prompt, temperature=0.8)
    except Exception as e:
        print(f"[错误] OllamaClient调用失败: {e}")
        return []

    # 解析LLM返回的JSON数组
    import re
    # 尝试直接解析
    qa_pairs = []
    try:
        qa_pairs = json.loads(raw_response.strip())
    except json.JSONDecodeError:
        # 尝试提取 [...] 数组
        match = re.search(r"\[.*\]", raw_response, re.DOTALL)
        if match:
            try:
                qa_pairs = json.loads(match.group())
            except json.JSONDecodeError:
                print("[警告] 无法解析LLM生成的JSON，原始输出已保存到日志")
                print(f"原始输出:\n{raw_response[:500]}...")
                return []

    print(f"  成功生成 {len(qa_pairs)} 个QA对")

    # 保存生成结果
    if output_path is None:
        safe_doc_id = document_id.replace("-", "_")[:12]
        output_path = str(RESULTS_DIR.parent / f"generated_dataset_{safe_doc_id}.json")

    RESULTS_DIR.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
    print(f"[保存] 生成数据集: {output_path}")

    return qa_pairs


# ==============================================================
# 主流程
# ==============================================================

def run_benchmark(
    methods: list,
    top_k: int,
    data_path: str,
    skip_generation: bool = False,
) -> dict:
    """
    主基准测试流程：对每个方法运行检索+生成评估，打印 Markdown 对比表格。

    参数:
        methods:          要评估的检索方法列表
        top_k:            检索参数
        data_path:        数据集路径
        skip_generation:  是否跳过生成评估（默认 False）

    返回:
        all_results 字典 {method: {"retrieval": {...}, "generation": {...}}}
    """
    # 加载数据集
    data_path = Path(data_path)
    if not data_path.exists():
        print(f"[错误] 数据集文件不存在: {data_path}")
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    print(f"[加载] 数据集: {data_path} | 共 {len(dataset)} 条")

    # 初始化数据库
    from backend.core.database import SessionLocal
    db = SessionLocal()

    all_results = {}

    try:
        for method in methods:
            print(f"\n{'='*70}")
            print(f"  基准测试方法: {method.upper()}")
            print(f"{'='*70}")

            # ── 检索评估 ──
            per_query_ret = run_retrieval_eval(method, dataset, top_k, db)
            retrieval_summary = aggregate_results(per_query_ret)
            print(f"\n[检索摘要] {method}:")
            for k, v in retrieval_summary.items():
                print(f"  {k}: {v:.4f}")

            # ── 生成评估 ──
            if skip_generation:
                print("[跳过] 生成评估（--skip_generation）")
                gen_summary = {}
                per_query_gen = []
            else:
                per_query_gen = run_generation_eval(dataset, top_k)
                gen_summary = aggregate_generation_results(per_query_gen)
                print(f"\n[生成摘要] {method}:")
                for k, v in gen_summary.items():
                    print(f"  {k}: {v:.4f}")

            # ── 保存结果 ──
            save_benchmark_results(
                method=method,
                retrieval_summary=retrieval_summary,
                generation_summary=gen_summary,
                per_query_retrieval=per_query_ret,
                per_query_generation=per_query_gen,
                top_k=top_k,
                dataset_path=data_path,
            )

            all_results[method] = {
                "retrieval": retrieval_summary,
                "generation": gen_summary,
            }

    finally:
        db.close()

    # 打印 Markdown 对比表格
    print_markdown_table(all_results)

    return all_results


# ==============================================================
# 命令行入口
# ==============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="RAG系统综合基准测试脚本（检索+生成评估）"
    )
    parser.add_argument(
        "--method",
        type=str,
        default="all",
        choices=SUPPORTED_METHODS + ["all"],
        help="要评估的检索方法，默认评估全部 (default: all)",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"检索top_k参数 (default: {DEFAULT_TOP_K})",
    )
    parser.add_argument(
        "--data",
        type=str,
        default=DEFAULT_DATASET,
        help=f"评估数据集路径 (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--skip_generation",
        action="store_true",
        default=False,
        help="跳过生成评估（仅运行检索评估），适合在没有运行API服务时使用",
    )
    parser.add_argument(
        "--generate_only",
        action="store_true",
        default=False,
        help="仅运行数据集生成模式，需配合 --document_id 使用",
    )
    parser.add_argument(
        "--document_id",
        type=str,
        default=None,
        help="用于生成QA数据集的文档ID（需配合 --generate_only）",
    )
    parser.add_argument(
        "--num_pairs",
        type=int,
        default=20,
        help="生成QA对的数量（默认20，配合 --generate_only 使用）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="生成数据集的输出路径（可选，配合 --generate_only 使用）",
    )

    args = parser.parse_args()

    # 模式1：仅生成数据集
    if args.generate_only:
        if not args.document_id:
            print("[错误] --generate_only 模式需要提供 --document_id 参数")
            sys.exit(1)
        generate_dataset_from_document(
            document_id=args.document_id,
            num_pairs=args.num_pairs,
            output_path=args.output,
        )
        sys.exit(0)

    # 模式2：基准测试
    if args.method == "all":
        methods_to_eval = SUPPORTED_METHODS
    else:
        methods_to_eval = [args.method]

    print(f"[启动] 基准测试 | 方法={methods_to_eval} | top_k={args.top_k}")
    print(f"[数据集] {args.data}")
    if args.skip_generation:
        print("[提示] 已启用 --skip_generation，将跳过生成评估")

    run_benchmark(
        methods=methods_to_eval,
        top_k=args.top_k,
        data_path=args.data,
        skip_generation=args.skip_generation,
    )
