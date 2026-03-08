import re
import uuid
from typing import Dict, List


class TextChunker:
    """
    文档切块模块（RAG核心模块）

    目标：
    1. 尽量保持语义完整
    2. chunk 不超过最大长度
    3. 保留 metadata (page/section)
    4. 支持 overlap 提升上下文连续性

    切块优先级：

    page
      ↓
    paragraph
      ↓
    sentence
      ↓
    hard split
    """

    def __init__(
        self,
        chunk_size: int = 800,
        overlap: int = 120
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

        # 标题检测
        self.heading_re = re.compile(
            r"^(#{1,6}\s+.*|[0-9]+\.\s+.*|[0-9]+\.[0-9]+\s+.*)",
            re.MULTILINE
        )

        # 句子切分
        self.sentence_re = re.compile(r'(?<=[.!?。！？])\s+')

        # markdown code block
        self.codeblock_re = re.compile(r"```.*?```", re.DOTALL)

        # markdown table
        self.table_line_re = re.compile(r"\|.*\|")

    # --------------------------------------------------
    # 检测 code block
    # --------------------------------------------------

    def _extract_code_blocks(self, text: str):

        blocks = []

        for m in self.codeblock_re.finditer(text):
            blocks.append((m.start(), m.end()))

        return blocks

    def _is_inside_block(self, index, blocks):

        for s, e in blocks:
            if s <= index <= e:
                return True

        return False

    # --------------------------------------------------
    # 按段落分割
    # --------------------------------------------------

    def _split_paragraphs(self, text: str):

        paragraphs = []

        parts = text.split("\n")

        buffer = []

        for line in parts:

            line = line.strip()

            if not line:
                if buffer:
                    paragraphs.append(" ".join(buffer))
                    buffer = []
                continue

            buffer.append(line)

        if buffer:
            paragraphs.append(" ".join(buffer))

        return paragraphs

    # --------------------------------------------------
    # 句子分割
    # --------------------------------------------------

    def _split_sentences(self, text: str):

        sentences = self.sentence_re.split(text)

        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    # --------------------------------------------------
    # 硬切分（最底层兜底）
    # --------------------------------------------------

    def _hard_split(self, text: str):

        chunks = []

        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk = text[start:end]

            chunks.append(chunk)

            start = end - self.overlap

        return chunks

    # --------------------------------------------------
    # paragraph chunking
    # --------------------------------------------------

    def _paragraph_chunk(self, paragraphs):

        chunks = []

        current = ""

        for p in paragraphs:

            if len(p) > self.chunk_size:

                # 段落过大 → 句子级拆分
                sentences = self._split_sentences(p)

                for s in sentences:

                    if len(current) + len(s) < self.chunk_size:

                        current += " " + s

                    else:

                        chunks.append(current.strip())

                        current = s

                continue

            if len(current) + len(p) < self.chunk_size:

                current += " " + p

            else:

                chunks.append(current.strip())

                current = p

        if current:
            chunks.append(current.strip())

        return chunks

    # --------------------------------------------------
    # overlap
    # --------------------------------------------------

    def _apply_overlap(self, chunks):

        if not chunks:
            return chunks

        overlapped = []

        for i, chunk in enumerate(chunks):

            if i == 0:
                overlapped.append(chunk)
                continue

            prev = overlapped[-1]

            prefix = prev[-self.overlap:]

            merged = prefix + " " + chunk

            overlapped.append(merged)

        return overlapped

    # --------------------------------------------------
    # 单页 chunk
    # --------------------------------------------------

    def _chunk_page(self, page):

        text = page["content"]

        # code block检测
        blocks = self._extract_code_blocks(text)

        paragraphs = self._split_paragraphs(text)

        chunks = self._paragraph_chunk(paragraphs)

        chunks = self._apply_overlap(chunks)

        return chunks

    # --------------------------------------------------
    # 主 chunk 函数
    # --------------------------------------------------

    def chunk(self, cleaned_doc: Dict) -> List[Dict]:

        pages = cleaned_doc.get("pages", [])

        results = []

        chunk_index = 0

        for page in pages:

            page_num = page.get("page_num")
            section = page.get("section")

            chunks = self._chunk_page(page)

            for c in chunks:

                if len(c) > self.chunk_size * 1.5:

                    # 极端情况：hard split
                    pieces = self._hard_split(c)

                else:

                    pieces = [c]

                for piece in pieces:

                    results.append({
                        "chunk_id": str(uuid.uuid4()),
                        "chunk_index": chunk_index,
                        "content": piece.strip(),
                        "page_start": page_num,
                        "page_end": page_num,
                        "section": section,
                        "metadata": {}
                    })

                    chunk_index += 1

        return results