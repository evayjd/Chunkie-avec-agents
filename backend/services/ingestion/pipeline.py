import os
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from backend.core.logging import logger
from backend.db.repositories.document_repo import DocumentRepository

from backend.services.ingestion.parsers.factory import ParserFactory
from backend.services.ingestion.cleaning.text_cleaner import TextCleaner
from backend.services.ingestion.chunking.text_chunker import TextChunker
from backend.services.ingestion.embedding.embedder import get_embedder
from backend.services.ingestion.indexing.vector_indexer import VectorIndexer


class IngestionPipeline:
    """
    文档处理流水线

    upload
        ↓
    parser
        ↓
    cleaner
        ↓
    chunker
        ↓
    embedding
        ↓
    indexing
    """

    def __init__(self, db: Session):

        self.db = db

        self.document_repo = DocumentRepository(db)

        self.cleaner = TextCleaner()

        self.chunker = TextChunker()

        self.embedder = get_embedder()

        self.indexer = VectorIndexer(db)

    # --------------------------------------------------
    # 主入口
    # --------------------------------------------------

    def ingest(self, file_path: str):

        logger.info(f"Ingestion started for file: {file_path}")

        filename = Path(file_path).name

        file_type = Path(file_path).suffix.lower()

        # ----------------------------------------------
        # parser
        # ----------------------------------------------

        parser = ParserFactory.get_parser(file_path)

        parsed_doc = parser.parse(file_path)

        logger.info("Parsing completed")

        # ----------------------------------------------
        # cleaner
        # ----------------------------------------------

        cleaned_doc = self.cleaner.clean(parsed_doc)

        logger.info("Cleaning completed")

        # ----------------------------------------------
        # 写入 document
        # ----------------------------------------------

        document = self.document_repo.create_document(
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            raw_text=parsed_doc["text"],
            cleaned_text=cleaned_doc["text"],
            metadata_json=parsed_doc.get("metadata")
        )

        document_id = document.id

        logger.info(f"Document stored: {document_id}")

        # ----------------------------------------------
        # chunking → embedding → indexing
        # 修复 Bug 4：任意步骤失败时回滚 DB 事务，避免孤立 document 记录
        # ----------------------------------------------

        try:
            chunks = self.chunker.chunk(cleaned_doc)
            logger.info(f"Chunking completed: {len(chunks)} chunks")

            texts = [c["content"] for c in chunks]
            embeddings = self.embedder.embed_texts(texts)
            logger.info("Embedding completed")

            self.indexer.index_chunks(
                document_id=document_id,
                chunks=chunks,
                embeddings=embeddings
            )
            logger.info("Vector indexing completed")

        except Exception as exc:
            logger.error(f"Pipeline failed after document creation: {exc}. Rolling back.")
            self.db.rollback()
            raise

        return document_id