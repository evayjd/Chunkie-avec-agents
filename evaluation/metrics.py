"""
evaluation/metrics.py

RAG系统评估指标模块
包含检索指标和生成指标，仅依赖Python标准库，无需安装额外ML框架。
"""

import math
from collections import Counter
from typing import Dict, List, Tuple


# ==============================================================
# 检索指标（Retrieval Metrics）
# ==============================================================

def hit_at_k(
    retrieved: List[str],
    relevant: List[str],
    k: int
) -> float:
    """
    Hit@K：判断Top-K检索结果中是否至少命中一个相关文档。

    参数:
        retrieved: 按相关性排序的检索结果ID列表
        relevant:  标准答案中的相关文档ID列表
        k:         截断位置

    返回:
        1.0 如果Top-K中包含至少一个相关文档，否则返回0.0
    """
    if k <= 0 or not relevant:
        return 0.0

    top_k = set(retrieved[:k])
    for rel_id in relevant:
        if rel_id in top_k:
            return 1.0
    return 0.0


def mrr(
    retrieved_lists: List[List[str]],
    relevant_lists: List[List[str]]
) -> float:
    """
    Mean Reciprocal Rank (MRR)：衡量第一个相关文档的平均倒数排名。

    参数:
        retrieved_lists: 多个查询的检索结果列表（每个元素是一次查询的排序结果）
        relevant_lists:  对应的相关文档列表

    返回:
        所有查询的平均倒数排名（float）
    """
    if not retrieved_lists:
        return 0.0

    reciprocal_ranks = []
    for retrieved, relevant in zip(retrieved_lists, relevant_lists):
        rr = 0.0
        relevant_set = set(relevant)
        for rank, doc_id in enumerate(retrieved, start=1):
            if doc_id in relevant_set:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

    return sum(reciprocal_ranks) / len(reciprocal_ranks)


def _dcg_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
    """
    计算单个查询的DCG@K（折扣累积增益）。
    相关文档的增益为1，不相关为0，使用 log2(rank+1) 折扣。
    """
    relevant_set = set(relevant)
    dcg = 0.0
    for rank, doc_id in enumerate(retrieved[:k], start=1):
        if doc_id in relevant_set:
            dcg += 1.0 / math.log2(rank + 1)
    return dcg


def ndcg_at_k(
    retrieved: List[str],
    relevant: List[str],
    k: int
) -> float:
    """
    NDCG@K（归一化折扣累积增益）：衡量检索结果排序质量。

    参数:
        retrieved: 按相关性排序的检索结果ID列表
        relevant:  标准相关文档ID列表
        k:         截断位置

    返回:
        NDCG@K 分数（0到1之间，1为完美排序）
    """
    if k <= 0 or not relevant:
        return 0.0

    dcg = _dcg_at_k(retrieved, relevant, k)

    # 理想排序：把所有相关文档排在最前面
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))

    if idcg == 0.0:
        return 0.0

    return dcg / idcg


def recall_at_k(
    retrieved: List[str],
    relevant: List[str],
    k: int
) -> float:
    """
    Recall@K：Top-K结果中召回了多少比例的相关文档。

    参数:
        retrieved: 按相关性排序的检索结果ID列表
        relevant:  标准相关文档ID列表
        k:         截断位置

    返回:
        召回率（0到1之间）
    """
    if not relevant or k <= 0:
        return 0.0

    top_k_set = set(retrieved[:k])
    hits = sum(1 for rel_id in relevant if rel_id in top_k_set)
    return hits / len(relevant)


def precision_at_k(
    retrieved: List[str],
    relevant: List[str],
    k: int
) -> float:
    """
    Precision@K：Top-K结果中有多少比例是相关文档。

    参数:
        retrieved: 按相关性排序的检索结果ID列表
        relevant:  标准相关文档ID列表
        k:         截断位置

    返回:
        精确率（0到1之间）
    """
    if k <= 0:
        return 0.0

    top_k = retrieved[:k]
    relevant_set = set(relevant)
    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)
    return hits / k


# ==============================================================
# 生成指标（Generation Metrics）
# ==============================================================

def exact_match(pred: str, gold: str) -> float:
    """
    精确匹配（Exact Match）：判断预测答案与标准答案是否完全一致（去空白后比较）。

    参数:
        pred: 模型生成的答案
        gold: 标准答案

    返回:
        1.0 如果完全匹配，否则0.0
    """
    return 1.0 if pred.strip() == gold.strip() else 0.0


def _tokenize(text: str) -> List[str]:
    """
    简单分词：按字符切分中文文本（每个汉字作为一个token），
    英文按空格切分，过滤空字符。
    """
    tokens = []
    for char in text:
        # 中文字符范围：\u4e00-\u9fff
        if '\u4e00' <= char <= '\u9fff':
            tokens.append(char)
        elif char.strip():
            # 非中文、非空白字符（如英文、数字）暂存
            tokens.append(char)
    # 合并连续非中文字符为单词（简单处理）
    merged: List[str] = []
    buffer = ""
    for tok in tokens:
        if '\u4e00' <= tok <= '\u9fff':
            if buffer:
                merged.extend(buffer.split())
                buffer = ""
            merged.append(tok)
        else:
            buffer += tok
    if buffer:
        merged.extend(buffer.split())
    return [t for t in merged if t]


def token_f1(pred: str, gold: str) -> float:
    """
    Token级别F1分数：以token为单位计算预测答案与标准答案的重叠程度。
    适用于中文问答的答案质量评估。

    参数:
        pred: 模型生成的答案
        gold: 标准答案

    返回:
        F1分数（0到1之间）
    """
    pred_tokens = _tokenize(pred)
    gold_tokens = _tokenize(gold)

    if not pred_tokens or not gold_tokens:
        return 0.0

    pred_counter = Counter(pred_tokens)
    gold_counter = Counter(gold_tokens)

    # 计算共同token数量（取最小值）
    common = sum((pred_counter & gold_counter).values())

    if common == 0:
        return 0.0

    precision = common / len(pred_tokens)
    recall = common / len(gold_tokens)

    f1 = 2 * precision * recall / (precision + recall)
    return f1


def _lcs_length(seq1: List[str], seq2: List[str]) -> int:
    """
    计算两个序列的最长公共子序列（LCS）长度。
    使用动态规划，时间复杂度O(m*n)。
    """
    m, n = len(seq1), len(seq2)
    # 使用滚动数组节省内存
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev, curr = curr, [0] * (n + 1)
    return prev[n]


def rouge_l(pred: str, gold: str) -> float:
    """
    ROUGE-L：基于最长公共子序列的F1分数，衡量生成文本与参考文本的结构相似度。

    参数:
        pred: 模型生成的答案
        gold: 标准答案

    返回:
        ROUGE-L F1分数（0到1之间）
    """
    pred_tokens = _tokenize(pred)
    gold_tokens = _tokenize(gold)

    if not pred_tokens or not gold_tokens:
        return 0.0

    lcs_len = _lcs_length(pred_tokens, gold_tokens)

    if lcs_len == 0:
        return 0.0

    precision = lcs_len / len(pred_tokens)
    recall = lcs_len / len(gold_tokens)

    rouge_l_score = 2 * precision * recall / (precision + recall)
    return rouge_l_score


def faithfulness_recall(answer: str, chunks: List[str]) -> float:
    """
    忠实性召回（Faithfulness Recall）：
    衡量生成答案中有多少token可以在检索到的chunks中找到对应依据。
    使用token重叠作为忠实性的代理指标。

    参数:
        answer: 模型生成的答案
        chunks: 检索到的文本块列表

    返回:
        忠实性分数（0到1之间，越高说明答案越多来自检索内容）
    """
    if not answer or not chunks:
        return 0.0

    answer_tokens = _tokenize(answer)
    if not answer_tokens:
        return 0.0

    # 将所有检索chunk合并为一个token集合
    chunk_token_counter: Counter = Counter()
    for chunk in chunks:
        chunk_token_counter.update(_tokenize(chunk))

    # 计算答案中有多少token在chunks中出现
    answer_counter = Counter(answer_tokens)
    overlap = sum((answer_counter & chunk_token_counter).values())

    return overlap / len(answer_tokens)


# ==============================================================
# 聚合计算函数（Aggregate Functions）
# ==============================================================

def compute_retrieval_metrics(
    results_list: List[Dict],
    k_values: List[int] = None
) -> Dict:
    """
    批量计算检索指标，汇总为平均值。

    参数:
        results_list: 每条数据的评估结果列表，每条包含：
            - "retrieved": 检索到的文档ID列表
            - "relevant":  相关文档ID列表
        k_values: 需要计算的K值列表，默认为 [1, 3, 5, 10]

    返回:
        汇总指标字典，包含各K值下的Hit@K、Recall@K、Precision@K、
        以及MRR和NDCG@5等指标的平均值
    """
    if k_values is None:
        k_values = [1, 3, 5, 10]

    if not results_list:
        return {}

    # 收集各指标的分数列表
    hit_scores: Dict[int, List[float]] = {k: [] for k in k_values}
    recall_scores: Dict[int, List[float]] = {k: [] for k in k_values}
    precision_scores: Dict[int, List[float]] = {k: [] for k in k_values}
    ndcg_scores: Dict[int, List[float]] = {k: [] for k in k_values}
    mrr_retrieved: List[List[str]] = []
    mrr_relevant: List[List[str]] = []

    for result in results_list:
        retrieved = result.get("retrieved", [])
        relevant = result.get("relevant", [])

        for k in k_values:
            hit_scores[k].append(hit_at_k(retrieved, relevant, k))
            recall_scores[k].append(recall_at_k(retrieved, relevant, k))
            precision_scores[k].append(precision_at_k(retrieved, relevant, k))
            ndcg_scores[k].append(ndcg_at_k(retrieved, relevant, k))

        mrr_retrieved.append(retrieved)
        mrr_relevant.append(relevant)

    # 计算平均值
    metrics: Dict = {}
    for k in k_values:
        n = len(hit_scores[k])
        metrics[f"hit@{k}"] = sum(hit_scores[k]) / n
        metrics[f"recall@{k}"] = sum(recall_scores[k]) / n
        metrics[f"precision@{k}"] = sum(precision_scores[k]) / n
        metrics[f"ndcg@{k}"] = sum(ndcg_scores[k]) / n

    # 计算整体MRR（跨所有查询）
    metrics["mrr"] = mrr(mrr_retrieved, mrr_relevant)

    return metrics


def compute_generation_metrics(results_list: List[Dict]) -> Dict:
    """
    批量计算生成指标，汇总为平均值。

    参数:
        results_list: 每条数据的评估结果列表，每条包含：
            - "pred":   模型生成的答案
            - "gold":   标准答案（ground truth）
            - "chunks": 检索到的文本块列表（用于忠实性计算）

    返回:
        汇总指标字典，包含以下平均值：
            - exact_match: 精确匹配率
            - token_f1:    Token级别F1
            - rouge_l:     ROUGE-L分数
            - faithfulness_recall: 忠实性召回率
    """
    if not results_list:
        return {}

    em_scores: List[float] = []
    f1_scores: List[float] = []
    rl_scores: List[float] = []
    faith_scores: List[float] = []

    for result in results_list:
        pred = result.get("pred", "")
        gold = result.get("gold", "")
        chunks = result.get("chunks", [])

        em_scores.append(exact_match(pred, gold))
        f1_scores.append(token_f1(pred, gold))
        rl_scores.append(rouge_l(pred, gold))
        faith_scores.append(faithfulness_recall(pred, chunks))

    n = len(results_list)
    return {
        "exact_match": sum(em_scores) / n,
        "token_f1": sum(f1_scores) / n,
        "rouge_l": sum(rl_scores) / n,
        "faithfulness_recall": sum(faith_scores) / n,
    }
