import re
import unicodedata
from collections import Counter
from typing import Dict, List, Set


class TextCleaner:
    """
    TextCleaner 在文档分块前执行标准化和结构清理。—— 升级版

    升级内容：
    1. detect_repeated_headers_footers 同时检测单行候选（原版只检测双行）。
    2. 新增 remove_toc_block：移除目录（Table of Contents / 目录）噪声块。
    3. 阈值从 >0.6 调整为 >=0.5，对只有一半页面有页眉的 PDF 也能覆盖。

    主要职责：
    - Unicode 标准化（处理全角/半角、特殊符号）
    - 移除控制字符
    - 智能识别并剔除跨页重复的页眉和页脚（单/双行）
    - 移除目录块
    - 修复段落内部的错误换行（支持中英文混排逻辑）
    - 压缩多余的空白字符
    """

    REPEAT_THRESHOLD = 0.5  # 出现在 ≥50% 页面即视为噪声（原为 >0.6）

    def __init__(self):
        # 移除不可见控制字符（ASCII 0-31，排除换行符 \n 和 \r 以保留段落结构）
        self.control_char_re = re.compile(r"[\x00-\x09\x0B\x0C\x0E-\x1F\x7F]")

        # 仅压缩水平空白（不跨越换行符），保留段落结构
        self.multi_space_re = re.compile(r"[^\S\n]+")

        # 句子结束标点 (涵盖中英文常用结束符)
        self.sentence_end_re = re.compile(r"[.!?。！？]$")

        # 匹配中文字符的正则表达式范围
        self.zh_re = re.compile(r"[\u4e00-\u9fa5]")

        # 目录行特征：文字后跟连续点（……）再跟页码数字
        # 兼容中英文 ToC 格式：  "Introduction . . . . . . 3"  /  "第一章……………1"
        self.toc_line_re = re.compile(
            r"^.{2,60}?(?:[\s.·。]{3,}|…{2,})\s*\d{1,4}\s*$"
        )

        # ToC 块标题行
        self.toc_header_re = re.compile(
            r"^(?:table\s+of\s+contents|contents|目\s*录)\s*$",
            re.IGNORECASE,
        )

    # --------------------------------------------------
    # Unicode 标准化
    # --------------------------------------------------

    def normalize_unicode(self, text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        text = self.control_char_re.sub("", text)
        return text

    # --------------------------------------------------
    # 空白字符标准化
    # --------------------------------------------------

    def normalize_whitespace(self, text: str) -> str:
        text = self.multi_space_re.sub(" ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    # --------------------------------------------------
    # 修复段落内的断行（中英优化版）
    # --------------------------------------------------

    def merge_broken_lines(self, text: str) -> str:
        lines = text.split("\n")
        merged_lines = []
        buffer = ""

        for line in lines:
            line = line.strip()

            if not line:
                if buffer:
                    merged_lines.append(buffer.strip())
                    buffer = ""
                continue

            if not buffer:
                buffer = line
                continue

            if self.sentence_end_re.search(buffer):
                merged_lines.append(buffer.strip())
                buffer = line
            else:
                last_char = buffer[-1]
                next_char = line[0]

                if self.zh_re.match(last_char) or self.zh_re.match(next_char):
                    buffer = buffer + line
                else:
                    buffer = buffer + " " + line

        if buffer:
            merged_lines.append(buffer.strip())

        return "\n".join(merged_lines)

    # --------------------------------------------------
    # 检测重复的页眉 / 页脚（升级：同时检测单行和双行候选）
    # --------------------------------------------------

    def detect_repeated_headers_footers(self, pages: List[Dict]) -> Dict:
        """
        检测跨页重复出现的页眉和页脚。

        升级：
        - 同时统计首/尾的 1 行和 2 行候选，取分数最高的形态。
        - 阈值从 >0.6 调整为 >=REPEAT_THRESHOLD (0.5)。
        """
        header1_ctr: Counter = Counter()
        header2_ctr: Counter = Counter()
        footer1_ctr: Counter = Counter()
        footer2_ctr: Counter = Counter()
        total_pages = len(pages)

        if total_pages < 2:
            return {"headers": set(), "footers": set()}

        for page in pages:
            lines = page.get("content", "").split("\n")
            lines = [l.strip() for l in lines if l.strip()]

            if len(lines) >= 1:
                header1_ctr[lines[0]] += 1
                footer1_ctr[lines[-1]] += 1
            if len(lines) >= 2:
                header2_ctr["\n".join(lines[:2])] += 1
                footer2_ctr["\n".join(lines[-2:])] += 1

        def _above_threshold(ctr: Counter) -> Set[str]:
            return {k for k, v in ctr.items() if v / total_pages >= self.REPEAT_THRESHOLD}

        headers_to_remove: Set[str] = _above_threshold(header1_ctr) | _above_threshold(header2_ctr)
        footers_to_remove: Set[str] = _above_threshold(footer1_ctr) | _above_threshold(footer2_ctr)

        return {"headers": headers_to_remove, "footers": footers_to_remove}

    # --------------------------------------------------
    # 移除检测到的页眉 / 页脚
    # --------------------------------------------------

    def remove_headers_footers(self, pages: List[Dict]) -> List[Dict]:
        detection = self.detect_repeated_headers_footers(pages)
        headers = detection["headers"]
        footers = detection["footers"]

        for page in pages:
            lines = page.get("content", "").split("\n")
            clean_lines = [l.strip() for l in lines]

            # 单行匹配
            if len(clean_lines) >= 1 and clean_lines[0] in headers:
                clean_lines = clean_lines[1:]
            # 双行匹配（在单行匹配之后再次尝试）
            if len(clean_lines) >= 2 and "\n".join(clean_lines[:2]) in headers:
                clean_lines = clean_lines[2:]

            if len(clean_lines) >= 1 and clean_lines[-1] in footers:
                clean_lines = clean_lines[:-1]
            if len(clean_lines) >= 2 and "\n".join(clean_lines[-2:]) in footers:
                clean_lines = clean_lines[:-2]

            page["content"] = "\n".join(clean_lines).strip()

        return pages

    # --------------------------------------------------
    # 移除目录块（升级新增）
    # --------------------------------------------------

    def remove_toc_block(self, pages: List[Dict]) -> List[Dict]:
        """
        识别并移除目录页。
        判断条件：某页有 >=5 行符合 toc_line_re，或以 toc_header_re 开头。
        整页内容被置空（后续 rebuild_document_text 会跳过空页）。
        """
        for page in pages:
            content = page.get("content", "")
            lines = [l.strip() for l in content.split("\n") if l.strip()]

            if not lines:
                continue

            # 检测目录标题行
            has_toc_header = bool(self.toc_header_re.match(lines[0]))

            # 统计符合 ToC 模式的行数
            toc_line_count = sum(1 for l in lines if self.toc_line_re.match(l))
            toc_ratio = toc_line_count / len(lines) if lines else 0

            if has_toc_header or toc_ratio >= 0.5:
                page["content"] = ""

        return pages

    # --------------------------------------------------
    # 清洗页面级文本
    # --------------------------------------------------

    def clean_pages(self, pages: List[Dict]) -> List[Dict]:
        """
        对每一页的内容进行标准化清洗。
        顺序：Unicode 标准化 → 空白压缩 → 断行修复
        """
        for page in pages:
            text = page.get("content", "")
            text = self.normalize_unicode(text)
            text = self.normalize_whitespace(text)
            text = self.merge_broken_lines(text)
            page["content"] = text
        return pages

    # --------------------------------------------------
    # 重建完整文档文本
    # --------------------------------------------------

    def rebuild_document_text(self, pages: List[Dict]) -> str:
        texts = [p["content"].strip() for p in pages if p.get("content", "").strip()]
        return "\n\n".join(texts)

    # --------------------------------------------------
    # 主 pipeline
    # --------------------------------------------------

    def clean(self, parsed_doc: Dict) -> Dict:
        """
        清洗流水线主入口。

        顺序：
        1. 移除页眉页脚（含单行检测）
        2. 移除目录块（新增）
        3. 精细清洗每页文本
        4. 重建文档
        """
        pages = parsed_doc.get("pages", [])

        pages = self.remove_headers_footers(pages)
        pages = self.remove_toc_block(pages)
        pages = self.clean_pages(pages)

        parsed_doc["text"] = self.rebuild_document_text(pages)
        parsed_doc["pages"] = pages

        return parsed_doc
