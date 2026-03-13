"""10-stage RAG retrieval pipeline."""
 

import time
import structlog
from rank_bm25 import BM25Okapi
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.providers.embedding import get_embedding_provider
from app.providers.reranker import get_reranker_provider
from app.repositories.chunk import ChunkRepository
from app.utils.text import count_tokens_approx

logger = structlog.get_logger(__name__)


def _rrf_score(rank: int, k: int = 60) -> float:
    """Reciprocal Rank Fusion score.

    Notes
    -----
    rank must start from 1, not 0.
    Theoretical max with k=60 is 1 / (60 + 1) = 1/61 ≈ 0.01639.
    """
    return 1.0 / (k + rank)


async def run_retrieval_pipeline(
    db: AsyncSession,
    query: str,
    document_ids: list[str] | None = None,
) -> tuple[list[dict], dict]:
    """Run retrieval pipeline. Returns (chunks_with_scores, metadata)."""
    s = get_settings()
    timing: dict[str, float] = {}
    chunk_repo = ChunkRepository(db)
    embed_provider = get_embedding_provider()

    logger.info(
        "retrieval_start",
        query=query,
        document_ids=document_ids,
    )

    # Stage 1: Query preprocessing
    t0 = time.perf_counter()
    query = query.strip()
    timing["preprocess"] = time.perf_counter() - t0

    # Stage 2: Dense retrieval
    t0 = time.perf_counter()
    query_vec = await embed_provider.embed_query(query)
    dense_results = await chunk_repo.similarity_search_with_scores(
        query_vec,
        document_ids,
        top_k=s.retrieval_dense_top_k,
    )

    # Apply similarity threshold — remove chunks that are not relevant to this query.
    # This is critical for dimension scoring: a query about "academic research" should
    # return few/no chunks if the KB has no academic content, driving the score down.
    sim_threshold = s.retrieval_similarity_threshold
    dense_results = [(c, sim) for c, sim in dense_results if sim >= sim_threshold]

    dense_chunks = [c for c, _ in dense_results]
    # Map chunk_id → cosine similarity for use in the output stage
    dense_score_map: dict[str, float] = {str(c.id): sim for c, sim in dense_results}

    timing["dense"] = time.perf_counter() - t0

    logger.info(
        "retrieval_dense_complete",
        query=query,
        n_dense=len(dense_chunks),
        sim_threshold=sim_threshold,
        dense_chunk_ids=[str(c.id) for c in dense_chunks[:10]],
        dense_scores=[round(dense_score_map[str(c.id)], 4) for c in dense_chunks[:10]],
        dense_preview=[c.content[:80] for c in dense_chunks[:5]],
    )

    # Stage 3: Sparse retrieval (BM25, in-memory over dense candidates)
    t0 = time.perf_counter()
    all_chunks = dense_chunks
    tokenized = [c.content.lower().split() for c in all_chunks]
    sparse_scores: list[tuple[int, float]] = []

    if tokenized:
        bm25 = BM25Okapi(tokenized)
        scores = bm25.get_scores(query.lower().split())
        sparse_scores = [
            (i, float(score))
            for i, score in sorted(
                enumerate(scores),
                key=lambda x: x[1],
                reverse=True,
            )[: s.retrieval_sparse_top_k]
        ]

    timing["sparse"] = time.perf_counter() - t0

    logger.info(
        "retrieval_sparse_complete",
        query=query,
        sparse_scores=[{"idx": i, "score": round(score, 6)} for i, score in sparse_scores[:10]],
    )

    # Stage 4: Hybrid RRF fusion
    t0 = time.perf_counter()
    rrf: dict[str, float] = {}

    # IMPORTANT: rank starts at 1, not 0
    for rank, chunk in enumerate(dense_chunks, start=1):
        key = str(chunk.id)
        rrf[key] = rrf.get(key, 0.0) + _rrf_score(rank) * s.retrieval_dense_weight

    for rank, (idx, _) in enumerate(sparse_scores, start=1):
        chunk = all_chunks[idx]
        key = str(chunk.id)
        rrf[key] = rrf.get(key, 0.0) + _rrf_score(rank) * s.retrieval_sparse_weight

    fused_ids = sorted(
        rrf.keys(),
        key=lambda cid: rrf[cid],
        reverse=True,
    )[: s.retrieval_fusion_top_k]

    chunk_map = {str(c.id): c for c in all_chunks}
    fused_chunks = [chunk_map[cid] for cid in fused_ids if cid in chunk_map]
    timing["fusion"] = time.perf_counter() - t0

    logger.info(
        "retrieval_fusion_complete",
        query=query,
        fused_ids=fused_ids,
        fused_scores={cid: round(rrf.get(cid, 0.0), 6) for cid in fused_ids},
        fused_preview=[
            {
                "chunk_id": str(c.id),
                "score": round(rrf.get(str(c.id), 0.0), 6),
                "text": c.content[:80],
            }
            for c in fused_chunks[:10]
        ],
    )

    # Stage 5: Metadata filter
    filtered = fused_chunks

    # Stage 6: Deduplication by text prefix
    t0 = time.perf_counter()
    seen: set[str] = set()
    deduped = []
    for c in filtered:
        key = c.content[:80]
        if key not in seen:
            seen.add(key)
            deduped.append(c)
    timing["dedup"] = time.perf_counter() - t0

    logger.info(
        "retrieval_dedup_complete",
        query=query,
        n_before=len(filtered),
        n_after=len(deduped),
        deduped_chunk_ids=[str(c.id) for c in deduped[:10]],
    )

    # Stage 7: Reranking
    t0 = time.perf_counter()
    reranked = deduped
    if s.reranker_enabled and deduped:
        reranker = get_reranker_provider()
        texts = [c.content for c in deduped]
        results = await reranker.rerank(
            query,
            texts,
            top_n=s.retrieval_final_top_k,
        )
        ordered_indices = [r["index"] for r in results if "index" in r]
        if ordered_indices:
            reranked = [deduped[i] for i in ordered_indices if i < len(deduped)]
    timing["rerank"] = time.perf_counter() - t0

    logger.info(
        "retrieval_rerank_complete",
        query=query,
        reranked_chunk_ids=[str(c.id) for c in reranked[:10]],
        reranked_preview=[c.content[:80] for c in reranked[:5]],
    )

    # Stage 8: Context packing (token budget)
    t0 = time.perf_counter()
    budget = s.retrieval_max_context_tokens
    packed = []
    used = 0

    for c in reranked[: s.retrieval_final_top_k]:
        tokens = count_tokens_approx(c.content)
        if used + tokens > budget:
            break
        packed.append(c)
        used += tokens

    timing["pack"] = time.perf_counter() - t0

    logger.info(
        "retrieval_pack_complete",
        query=query,
        packed_chunk_ids=[str(c.id) for c in packed],
        used_tokens=used,
        budget=budget,
    )

    # Stage 9: Citation alignment
    t0 = time.perf_counter()
    chunks_out = []
    for i, c in enumerate(packed):
        chunks_out.append(
            {
                "citation_number": i + 1,
                "chunk_id": str(c.id),
                "document_id": str(c.document_id),
                "text": c.content,
                "char_start": c.char_start,
                "char_end": c.char_end,
                # RRF rank-fusion score (kept for logging/debugging)
                "score": rrf.get(str(c.id), 0.0),
                # Actual cosine similarity to this dimension's query — used for scoring.
                # This is query-dependent and reflects true relevance, unlike RRF which
                # only captures rank position and is nearly identical across dimensions.
                "dense_score": dense_score_map.get(str(c.id), 0.0),
            }
        )
    timing["citation_align"] = time.perf_counter() - t0

    # Stage 10: Output
    timing["total"] = sum(timing.values())

    logger.info(
        "retrieval_complete",
        query=query,
        n_chunks=len(chunks_out),
        top_scores=[round(c["score"], 6) for c in chunks_out[:5]],
        top_chunk_ids=[c["chunk_id"] for c in chunks_out[:5]],
        top_chunk_preview=[c["text"][:80] for c in chunks_out[:5]],
        timing=timing,
    )

    return chunks_out, timing