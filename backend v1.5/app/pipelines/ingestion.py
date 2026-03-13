"""Document ingestion pipeline: parse → chunk → embed → store."""
 
import hashlib
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DocumentStatus
from app.core.exceptions import DocumentProcessingError
from app.pipelines.parsers import parse_document
from app.pipelines.chunker import chunk_document
from app.providers.embedding import get_embedding_provider
from app.repositories.document import DocumentRepository
from app.repositories.chunk import ChunkRepository

logger = structlog.get_logger(__name__)


async def run_ingestion_pipeline(
    db: AsyncSession,
    doc_id: str,
    filename: str,
    content: bytes,
) -> None:
    """Full ingestion: parse → chunk → embed → persist."""
    doc_repo = DocumentRepository(db)
    chunk_repo = ChunkRepository(db)

    try:
        await doc_repo.update_status(doc_id, DocumentStatus.PROCESSING)

        # 1. Parse
        logger.info("ingestion_parse", doc_id=str(doc_id), filename=filename)
        raw_text = parse_document(filename, content)

        # 2. Chunk
        chunks = chunk_document(raw_text)
        logger.info("ingestion_chunked", doc_id=str(doc_id), n_chunks=len(chunks))

        # 3. Embed
        provider = get_embedding_provider()
        texts = [c["text"] for c in chunks]
        embeddings = await provider.embed_texts(texts)

        # 4. Persist chunks
        chunk_dicts = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            text = chunk["text"]
            chunk_dicts.append(
                {
                    "document_id": str(doc_id),
                    "chunk_index": i,
                    "content": text,
                    "content_hash": hashlib.sha256(text.encode()).hexdigest(),
                    "embedding": emb,
                    "char_start": chunk.get("char_start", 0),
                    "char_end": chunk.get("char_end", 0),
                    "token_count": chunk.get("token_count", 0),
                }
            )

        await chunk_repo.bulk_create(chunk_dicts)

        # 5. Update document metadata
        doc = await doc_repo.get(doc_id)
        if doc:
            doc.total_chunks = len(chunks)

        await doc_repo.update_status(doc_id, DocumentStatus.INDEXED)
        logger.info("ingestion_complete", doc_id=str(doc_id))

    except Exception as exc:
        logger.error("ingestion_failed", doc_id=str(doc_id), error=str(exc))
        await doc_repo.update_status(
            doc_id, DocumentStatus.FAILED, error=str(exc)
        )
        raise DocumentProcessingError(filename=filename, reason=str(exc)) from exc
