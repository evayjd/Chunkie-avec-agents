from pathlib import Path
from typing import Any, Dict

from backend.services.ingestion.parsers.base import BaseParser

#没做复杂的ast解析，先保留文本内容，后续做标题级chunking再升级
class MarkdownParser(BaseParser):
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
                "parser": "markdown",
                "source_path": str(path),
            },
        }