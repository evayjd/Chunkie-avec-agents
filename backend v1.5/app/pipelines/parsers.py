"""Document parsers: PDF, Markdown, plain text, DOCX."""
 
import io
import structlog

logger = structlog.get_logger(__name__)


def parse_pdf(content: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(content))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n\n".join(pages)
    except Exception as exc:
        logger.error("pdf_parse_error", error=str(exc))
        raise


def parse_markdown(content: bytes) -> str:
    return content.decode("utf-8", errors="replace")


def parse_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="replace")


def parse_docx(content: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as exc:
        logger.error("docx_parse_error", error=str(exc))
        raise


def parse_document(filename: str, content: bytes) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    parsers = {
        "pdf": parse_pdf,
        "md": parse_markdown,
        "txt": parse_txt,
        "docx": parse_docx,
    }
    parser = parsers.get(ext)
    if not parser:
        raise ValueError(f"Unsupported file type: {ext}")
    return parser(content)
