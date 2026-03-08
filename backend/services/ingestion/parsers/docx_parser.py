from pathlib import Path
from typing import Any, Dict

from docx import Document as DocxDocument

from backend.services.ingestion.parsers.base import BaseParser


class DOCXParser(BaseParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        doc = DocxDocument(str(path))

        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)

        full_text = "\n".join(paragraphs)

        return {
            "text": full_text,
            "pages": [
                {
                    "page_num": 1,
                    "content": full_text,
                    "section": None,
                }
            ],
            "metadata": {
                "parser": "docx",
                "source_path": str(path),
                "paragraph_count": len(paragraphs),
            },
        }