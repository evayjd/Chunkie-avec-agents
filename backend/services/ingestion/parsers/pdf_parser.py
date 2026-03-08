from pathlib import Path
from typing import Any, Dict, List

import fitz

from backend.services.ingestion.parsers.base import BaseParser


class PDFParser(BaseParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        doc = fitz.open(str(path))

        pages: List[Dict[str, Any]] = []
        full_text_parts: List[str] = []

        for i, page in enumerate(doc):
            text = page.get_text("text")
            text = text.strip()

            pages.append(
                {
                    "page_num": i + 1,
                    "content": text,
                    "section": None,
                }
            )

            if text:
                full_text_parts.append(text)

        full_text = "\n\n".join(full_text_parts)

        metadata = {
            "parser": "pdf",
            "source_path": str(path),
            "page_count": len(doc),
        }

        doc.close()

        return {
            "text": full_text,
            "pages": pages,
            "metadata": metadata,
        }