from pathlib import Path

from backend.services.ingestion.parsers.base import BaseParser
from backend.services.ingestion.parsers.docx_parser import DOCXParser
from backend.services.ingestion.parsers.html_parser import HTMLParser
from backend.services.ingestion.parsers.md_parser import MarkdownParser
from backend.services.ingestion.parsers.pdf_parser import PDFParser
from backend.services.ingestion.parsers.txt_parser import TXTParser


class ParserFactory:
    _parsers = {
        ".txt": TXTParser,
        ".md": MarkdownParser,
        ".markdown": MarkdownParser,
        ".html": HTMLParser,
        ".htm": HTMLParser,
        ".docx": DOCXParser,
        ".pdf": PDFParser,
    }

    @classmethod
    def get_parser(cls, file_path: str) -> BaseParser:
        suffix = Path(file_path).suffix.lower()

        parser_cls = cls._parsers.get(suffix)
        if parser_cls is None:
            supported = ", ".join(sorted(cls._parsers.keys()))
            raise ValueError(
                f"Unsupported file type: {suffix}. Supported types: {supported}"
            )

        return parser_cls()