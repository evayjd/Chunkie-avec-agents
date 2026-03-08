from pathlib import Path
from typing import Any, Dict

from backend.services.ingestion.parsers.base import BaseParser


class TXTParser(BaseParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        text = path.read_text(encoding="utf-8", errors="ignore")

        return {
            "text": text,
            "pages": [
                {
                    "page_num": 1,
                    "content": text,
                    "section": None,
                }
            ],
            "metadata": {
                "parser": "txt",
                "source_path": str(path),
            },
        }