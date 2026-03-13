import re
import uuid
from typing import Dict, List, Optional, Tuple


class TextChunker:
    """
    文档切块模块（RAG核心模块）—— 升级版

    升级内容：
    1. Section boundary split：将 Markdown 标题 / 编号章节作为硬切分边界，
       并将当前 heading 写入 chunk metadata，方便检索时展示章节上下文。
    2. Density filter：丢弃标点/空白比例 >70% 的噪声块（常见于扫描版 PDF）。
    3. 调小默认参数：chunk_size=600, overlap=100，对 BGE-small-en 精度更友好。
    4. 原有语义切块逻辑（段落→句子→硬切）保持不变。

    切块优先级：
    page
      ↓
    section / heading boundary
      ↓
    paragraph
      ↓
    sentence
      ↓
    hard split
    """

    MIN_CHUNK_LEN = 30      # 过短的 chunk 没有检索价值
    MAX_NOISE_RATIO = 0.70  # 噪声密度阈值（标点+空白占比）

    def __init__(
        self,
        chunk_size: int = 600,
        overlap: int = 100,
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

        # 标题检测（Markdown heading / 数字编号章节）
        self.heading_re = re.compile(
            r"^(#{1,6}\s+.+|[0-9]+\.\s+.+|[0-9]+\.[0-9]+\s+.+)",
            re.MULTILINE,
        )

        # Section boundary：作为硬切分点的标题行（同上，但用于整段文本分割）
        self.section_re = re.compile(
            r"^(?:#{1,6}\s+|[0-9]+(?:\.[0-9]+)*\s+)\S",
            re.MULTILINE,
        )

        # 句子切分（中英文句尾标点后跟空白）
        self.sentence_re = re.compile(r"(?<=[.!?。！？])\s+")

        # markdown code block
        self.codeblock_re = re.compile(r"```.*?```", re.DOTALL)

        # 用于噪声检测：标点和空白字符
        self.noise_char_re = re.compile(r"[\W\s]")

    # --------------------------------------------------
    # 噪声密度过滤
    # --------------------------------------------------

    def _is_noisy(self, text: str) -> bool:
        """
        如果 chunk 中标点/空白占比超过阈值则认为是噪声，丢弃。
        主要清除扫描版 PDF 产生的乱码行和纯分隔线块。
        """
        if not text:
            return True
        noise_count = len(self.noise_char_re.findall(text))
        return noise_count / len(text) > self.MAX_NOISE_RATIO

    # --------------------------------------------------
    # 检测 code block 区间
    # --------------------------------------------------

    def _extract_code_blocks(self, text: str) -> List[Tuple[int, int]]:
        return [(m.start(), m.end()) for m in self.codeblock_re.finditer(text)]

    # --------------------------------------------------
    # Section boundary split（在段落切分之前）
    # --------------------------------------------------

    def _split_by_sections(self, text: str) -> List[Dict]:
        """
        按章节标题将文本拆分为若干段落块，每块携带当前 heading 作为 section_context。
        返回列表：[{"content": str, "heading": Optional[str]}]
        """
        matches = list(self.section_re.finditer(text))
        if not matches:
            return [{"content": text, "heading": None}]

        sections: List[Dict] = []
        prev_end = 0
        prev_heading: Optional[str] = None

        for m in matches:
            # 标题行之前的文本属于上一节
            before = text[prev_end:m.start()].strip()
            if before:
                sections.append({"content": before, "heading": prev_heading})

            # 提取标题行文字
            heading_line = m.group().strip()
            prev_heading = heading_line
            prev_end = m.start()

        # 最后一节
        remaining = text[prev_end:].strip()
        if remaining:
            sections.append({"content": remaining, "heading": prev_heading})

        return sections

    # --------------------------------------------------
    # 按段落分割（感知 code block，不拆断它）
    # --------------------------------------------------

    def _split_paragraphs(self, text: str) -> List[str]:
        """
        按空行拆分段落；如果整个 code block 跨越多段，将其作为一个整体保留。
        """
        code_blocks = self._extract_code_blocks(text)

        protected: List[Tuple[int, int, str]] = []
        placeholder_map: Dict[str, str] = {}

        offset_shift = 0
        working = text
        for s, e in sorted(code_blocks, key=lambda x: x[0]):
            token = f"__CODEBLOCK_{uuid.uuid4().hex}__"
            snippet = text[s:e]
            placeholder_map[token] = snippet
            working = working[:s - offset_shift] + token + working[e - offset_shift:]
            offset_shift += (e - s) - len(token)

        parts = working.split("\n\n")
        paragraphs = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            for token, code in placeholder_map.items():
                part = part.replace(token, code)
            paragraphs.append(part)

        return paragraphs

    # --------------------------------------------------
    # 句子分割
    # --------------------------------------------------

    def _split_sentences(self, text: str) -> List[str]:
        sentences = self.sentence_re.split(text)
        return [s.strip() for s in sentences if s.strip()]

    # --------------------------------------------------
    # 硬切分（最底层兜底）
    # --------------------------------------------------

    def _hard_split(self, text: str) -> List[str]:
        chunks = []
        start = 0
        length = len(text)
        while start < length:
            end = min(start + self.chunk_size, length)
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            advance = max(1, self.chunk_size - self.overlap)
            start += advance
        return chunks

    # --------------------------------------------------
    # paragraph chunking
    # --------------------------------------------------

    def _paragraph_chunk(self, paragraphs: List[str]) -> List[str]:
        chunks: List[str] = []
        current = ""

        for p in paragraphs:
            if len(p) > self.chunk_size:
                sentences = self._split_sentences(p)
                for s in sentences:
                    if len(current) + len(s) + 1 <= self.chunk_size:
                        current = (current + " " + s).strip() if current else s
                    else:
                        if current:
                            chunks.append(current.strip())
                        if len(s) > self.chunk_size:
                            pieces = self._hard_split(s)
                            chunks.extend(pieces[:-1])
                            current = pieces[-1] if pieces else ""
                        else:
                            current = s
                continue

            if len(current) + len(p) + 1 <= self.chunk_size:
                current = (current + "\n\n" + p).strip() if current else p
            else:
                if current:
                    chunks.append(current.strip())
                current = p

        if current:
            chunks.append(current.strip())

        return chunks

    # --------------------------------------------------
    # overlap
    # --------------------------------------------------

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        if not chunks:
            return chunks

        overlapped: List[str] = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped.append(chunk)
                continue
            prev = overlapped[-1]
            prefix = prev[-self.overlap:].strip()
            merged = (prefix + " " + chunk).strip() if prefix else chunk
            overlapped.append(merged)

        return overlapped

    # --------------------------------------------------
    # 单页 chunk（带 heading_context）
    # --------------------------------------------------

    def _chunk_page(self, page: Dict) -> List[Dict]:
        """
        返回列表：[{"content": str, "heading_context": Optional[str]}]
        """
        text = page.get("content", "").strip()
        if not text:
            return []

        # 先按 section 边界拆分，保留 heading 元信息
        sections = self._split_by_sections(text)
        result: List[Dict] = []

        for section in sections:
            section_text = section["content"]
            heading = section["heading"]

            paragraphs = self._split_paragraphs(section_text)
            raw_chunks = self._paragraph_chunk(paragraphs)
            raw_chunks = self._apply_overlap(raw_chunks)

            for c in raw_chunks:
                result.append({"content": c, "heading_context": heading})

        return result

    # --------------------------------------------------
    # 主 chunk 函数
    # --------------------------------------------------

    def chunk(self, cleaned_doc: Dict) -> List[Dict]:
        pages = cleaned_doc.get("pages", [])
        results: List[Dict] = []
        chunk_index = 0

        for page in pages:
            page_num = page.get("page_num")
            section = page.get("section")

            page_chunks = self._chunk_page(page)

            for item in page_chunks:
                c = item["content"]
                heading_context = item.get("heading_context")

                # 极端情况：hard split
                if len(c) > self.chunk_size * 1.5:
                    pieces = self._hard_split(c)
                else:
                    pieces = [c]

                for piece in pieces:
                    content = piece.strip()

                    # 过滤空块和过短无意义块
                    if len(content) < self.MIN_CHUNK_LEN:
                        continue

                    # 噪声密度过滤（升级新增）
                    if self._is_noisy(content):
                        continue

                    results.append({
                        "chunk_id": str(uuid.uuid4()),
                        "chunk_index": chunk_index,
                        "content": content,
                        "page_start": page_num,
                        "page_end": page_num,
                        "section": section or heading_context,  # 优先用 page section，其次用检测到的 heading
                        "metadata": {
                            "heading_context": heading_context,
                        },
                    })

                    chunk_index += 1

        return results
