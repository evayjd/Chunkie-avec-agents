"""Persona roast / analysis service."""
 

import json
import uuid
import structlog
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.constants import ROAST_SYSTEM_PROMPT, PersonaDimension
from app.core.scoring_rules import calculate_dimension_score
from app.pipelines.retrieval import run_retrieval_pipeline
from app.providers.llm import get_llm_provider
from app.repositories.document import DocumentRepository
from app.schemas.roast import RoastProfileOut, DimensionScoreOut, PersonaTagOut

logger = structlog.get_logger(__name__)

# 更自然语言的 query，比“逗号关键词列表”更利于 embedding 区分
_DIMENSION_QUERIES = {
    PersonaDimension.BUILDER_ENERGY: "关于编程项目、代码实现、系统构建、工程实践和创造输出的内容",
    PersonaDimension.ACADEMIC_INTENSITY: "关于研究、论文、理论分析、学术思考和深度学习笔记的内容",
    PersonaDimension.PERFECTIONISM: "关于追求完美、重视细节、代码优化、规范、最佳实践和反复改进的内容",
    PersonaDimension.MULTILINGUAL_FLEX: "关于中英法等多语言切换、双语表达、翻译或混合书写的内容",
    PersonaDimension.CAREER_SIGNALING: "关于职业发展、实习、简历、面试、能力证明、晋升和未来工作的内容",
    PersonaDimension.AESTHETIC_OBSESSION: "关于设计、美感、UI、视觉风格、排版、页面美化和审美表达的内容",
    PersonaDimension.CHAOS_FACTOR: "关于混乱笔记、临时想法、随机记录、快速实验、临时 hack 和未整理内容的内容",
    PersonaDimension.OVERENGINEERING_RISK: "关于架构设计、抽象层次、框架选择、设计模式和过度工程化讨论的内容",
}


class RoastService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def generate_roast(
        self,
        document_ids: list[uuid.UUID] | None = None,
        language: str = "zh",
    ) -> RoastProfileOut:
        s = get_settings()
        doc_repo = DocumentRepository(self._db)
        docs = await doc_repo.list_all(limit=100)

        if document_ids:
            docs = [d for d in docs if d.id in document_ids]

        if not docs:
            raise ValueError("没有可分析的文档")

        logger.info(
            "roast_generation_start",
            language=language,
            document_ids=[str(d.id) for d in docs],
            n_docs=len(docs),
        )

        # Score dimensions
        dimension_scores: dict[str, DimensionScoreOut] = {}
        evidence_chunks: list[dict] = []
        dimension_debug: dict[str, dict] = {}

        for dim, query in _DIMENSION_QUERIES.items():
            print("\n================ ROAST DIMENSION DEBUG ================")
            print("DIMENSION:", dim.value)
            print("QUERY:", query)

            logger.info(
                "roast_dimension_retrieval_start",
                dimension=dim.value,
                query=query,
            )

            chunks, timing = await run_retrieval_pipeline(
                self._db,
                query,
                [str(d.id) for d in docs],
            )

            top_scores = [round(c.get("score", 0.0), 6) for c in chunks[:5]]
            top_chunk_ids = [c.get("chunk_id", "") for c in chunks[:5]]
            top_preview = [c.get("text", "")[:100] for c in chunks[:3]]

            print("TOP SCORES:", top_scores)
            print("TOP CHUNK IDS:", top_chunk_ids)
            print("TOP PREVIEW:")
            for i, text in enumerate(top_preview, start=1):
                print(f"  [{i}] {text}")

            score = calculate_dimension_score(chunks)

            print("FINAL SCORE:", score)
            print("======================================================\n")

            logger.info(
                "roast_dimension_retrieval_complete",
                dimension=dim.value,
                query=query,
                top_scores=top_scores,
                top_chunk_ids=top_chunk_ids,
                top_preview=top_preview,
                final_score=score,
                timing=timing,
            )

            dimension_scores[dim.value] = DimensionScoreOut(
                dimension=dim.value,
                score=score,
                label=dim.value.replace("_", " ").title(),
                evidence=chunks[0].get("text", "") if chunks else "",
            )

            # 每个维度只取前2个证据供 roast 文本使用
            evidence_chunks.extend(chunks[:2])

            dimension_debug[dim.value] = {
                "query": query,
                "top_scores": top_scores,
                "top_chunk_ids": top_chunk_ids,
                "top_preview": top_preview,
                "final_score": score,
            }

        logger.info(
            "roast_all_dimensions_scored",
            dimension_debug=dimension_debug,
        )

        # Build LLM prompt for roast
        context = "\n\n".join(
            f"[{c['citation_number']}] {c['text'][:200]}"
            for c in evidence_chunks[:10]
        )
        scores_summary = "\n".join(
            f"- {k}: {v.score}" for k, v in dimension_scores.items()
        )

        system = ROAST_SYSTEM_PROMPT.get(language, ROAST_SYSTEM_PROMPT["zh"])
        prompt = (
            f"文档摘录：\n{context}\n\n"
            f"维度评分：\n{scores_summary}\n\n"
            f"请生成一段幽默而有洞察力的人格分析（roast），并提取5个人格标签（JSON格式）。\n"
            f"返回格式：\n"
            f"{{\"roast\": \"...\", \"tags\": ["
            f"{{\"tag\": \"...\", \"label\": \"...\", \"confidence\": 0.9, "
            f"\"evidence_snippet\": \"...\", \"citation_number\": 1}}]}}"
        )

        logger.info(
            "roast_llm_prompt_ready",
            scores_summary=scores_summary,
            context_preview=context[:1000],
        )

        llm = get_llm_provider()
        raw = await llm.chat_completion(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ]
        )

        logger.info(
            "roast_llm_response_received",
            raw_preview=raw[:1000],
        )

        # Parse response — strip markdown code fences before extracting JSON
        def _extract_json(text: str) -> dict:
            import re

            stripped = re.sub(r"```(?:json)?\s*", "", text).strip()
            start = stripped.find("{")
            end = stripped.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("no JSON object found")
            return json.loads(stripped[start:end])

        try:
            parsed = _extract_json(raw)
            roast_text = parsed.get("roast", "").strip() or raw
            tags_raw = parsed.get("tags", [])
        except Exception as e:
            logger.warning(
                "roast_json_parse_failed",
                error=str(e),
                raw_preview=raw[:1000],
            )
            roast_text = raw.strip()
            tags_raw = []

        tags = [PersonaTagOut(**t) for t in tags_raw if isinstance(t, dict)]

        logger.info(
            "roast_generation_complete",
            roast_preview=roast_text[:500],
            n_tags=len(tags),
            dimension_scores={k: v.score for k, v in dimension_scores.items()},
        )

        return RoastProfileOut(
            id=str(uuid.uuid4()),
            roast_text=roast_text,
            dimension_scores=list(dimension_scores.values()),
            persona_tags=tags,
            citations=[],
            language=language,
            tone="playful",
            created_at=datetime.utcnow(),
        )