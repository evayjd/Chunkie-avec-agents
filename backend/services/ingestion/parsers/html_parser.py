from pathlib import Path
from typing import Any, Dict

from bs4 import BeautifulSoup

from backend.services.ingestion.parsers.base import BaseParser


class HTMLParser(BaseParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        html = path.read_text(encoding="utf-8", errors="ignore")

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        title = soup.title.string.strip() if soup.title and soup.title.string else None

        return {
            "text": text,
            "pages": [
                {
                    "page_num": 1,
                    "content": text,
                    "section": title,
                }
            ],
            "metadata": {
                "parser": "html",
                "source_path": str(path),
                "title": title,
            },
        }