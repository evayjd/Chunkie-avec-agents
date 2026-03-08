import re
import unicodedata
from collections import Counter
from typing import Dict, List


class TextCleaner:
    """
    TextCleaner 在文档分块前执行标准化和结构清理。

    主要职责：
    - Unicode 标准化（处理全角/半角、特殊符号）
    - 移除控制字符
    - 智能识别并剔除跨页重复的页眉和页脚
    - 修复段落内部的错误换行（支持中英文混排逻辑）
    - 压缩多余的空白字符
    """

    def __init__(self):
        # 移除不可见控制字符（ASCII 0-31 以及 127）
        self.control_char_re = re.compile(r"[\x00-\x1F\x7F]")

        # 检测多个连续空格
        self.multi_space_re = re.compile(r"\s+")

        # 句子结束标点 (涵盖中英文常用结束符)
        self.sentence_end_re = re.compile(r"[.!?。！？]$")

        # 匹配中文字符的正则表达式范围
        self.zh_re = re.compile(r"[\u4e00-\u9fa5]")

    # --------------------------------------------------
    # Unicode 标准化
    # --------------------------------------------------

    def normalize_unicode(self, text: str) -> str:
        """
        标准化 Unicode 字符并移除控制字符。
        """
        # 使用 NFKC 将全角字符转为半角，并统一兼容字符
        text = unicodedata.normalize("NFKC", text)
        # 移除不可见字符
        text = self.control_char_re.sub("", text)
        return text

    # --------------------------------------------------
    # 空白字符标准化
    # --------------------------------------------------

    def normalize_whitespace(self, text: str) -> str:
        """
        将多个连续的空白字符压缩为一个空格。
        """
        text = self.multi_space_re.sub(" ", text)
        return text.strip()

    # --------------------------------------------------
    # 修复段落内的断行（中英优化版）
    # --------------------------------------------------

    def merge_broken_lines(self, text: str) -> str:
        """
        合并段落内部的异常换行。
        
        优化点：
        - 识别句尾标点，判断是否为自然换行。
        - 针对中英文混排：中文相连不加空格，英文相连保留空格。
        """
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

            # 如果缓冲区以句尾标点结束，认为是段落自然结束
            if self.sentence_end_re.search(buffer):
                merged_lines.append(buffer.strip())
                buffer = line
            else:
                # 检查连接处的字符类型
                last_char = buffer[-1]
                next_char = line[0]

                # 如果连接处任一侧是中文，则直接合并（不加空格）
                if self.zh_re.match(last_char) or self.zh_re.match(next_char):
                    buffer = buffer + line
                else:
                    # 如果两侧都是西文字符，合并时添加空格分隔单词
                    buffer = buffer + " " + line

        if buffer:
            merged_lines.append(buffer.strip())

        return "\n".join(merged_lines)

    # --------------------------------------------------
    # 检测重复的页眉 / 页脚
    # --------------------------------------------------

    def detect_repeated_headers_footers(self, pages: List[Dict]) -> Dict:
        """
        检测跨页重复出现的页眉和页脚。
        策略：统计每页首尾两行出现频率，超过 60% 页面即判定为噪声。
        """
        header_candidates = Counter()
        footer_candidates = Counter()
        total_pages = len(pages)

        if total_pages < 2:  # 单页文档无需剔除
            return {"headers": set(), "footers": set()}

        for page in pages:
            lines = page.get("content", "").split("\n")
            lines = [l.strip() for l in lines if l.strip()]

            if len(lines) >= 2:
                # 记录前两行作为候选页眉
                header = "\n".join(lines[:2])
                header_candidates[header] += 1
                # 记录最后两行作为候选页脚
                footer = "\n".join(lines[-2:])
                footer_candidates[footer] += 1

        headers_to_remove = {
            h for h, count in header_candidates.items()
            if count / total_pages > 0.6
        }
        footers_to_remove = {
            f for f, count in footer_candidates.items()
            if count / total_pages > 0.6
        }

        return {"headers": headers_to_remove, "footers": footers_to_remove}

    # --------------------------------------------------
    # 移除检测到的页眉 / 页脚
    # --------------------------------------------------

    def remove_headers_footers(self, pages: List[Dict]) -> List[Dict]:
        """
        从页面内容中移除检测到的页眉和页脚。
        """
        detection = self.detect_repeated_headers_footers(pages)
        headers = detection["headers"]
        footers = detection["footers"]

        for page in pages:
            lines = page.get("content", "").split("\n")
            # 预清理空行以便匹配
            clean_lines = [l.strip() for l in lines]
            
            # 匹配逻辑需与 detection 阶段严格对应
            current_header = "\n".join(clean_lines[:2]) if len(clean_lines) >= 2 else ""
            current_footer = "\n".join(clean_lines[-2:]) if len(clean_lines) >= 2 else ""

            # 如果匹配，移除对应的行
            if current_header in headers:
                clean_lines = clean_lines[2:]
            if current_footer in footers:
                clean_lines = clean_lines[:-2]

            page["content"] = "\n".join(clean_lines).strip()

        return pages

    # --------------------------------------------------
    # 清洗页面级文本
    # --------------------------------------------------

    def clean_pages(self, pages: List[Dict]) -> List[Dict]:
        """
        对每一页的内容进行标准化清洗。
        """
        for page in pages:
            text = page.get("content", "")
            # 执行清洗流程
            text = self.normalize_unicode(text)
            text = self.merge_broken_lines(text)
            text = self.normalize_whitespace(text)
            page["content"] = text
        return pages

    # --------------------------------------------------
    # 重建完整文档文本
    # --------------------------------------------------

    def rebuild_document_text(self, pages: List[Dict]) -> str:
        """
        将清洗后的各页内容重新拼接为完整文本，使用双换行区分页面。
        """
        texts = [p["content"].strip() for p in pages if p.get("content", "").strip()]
        return "\n\n".join(texts)

    # --------------------------------------------------
    # 主要pipeline
    # --------------------------------------------------

    def clean(self, parsed_doc: Dict) -> Dict:
        """
        清洗流水线主入口。
        """
        pages = parsed_doc.get("pages", [])

        # 1. 移除噪声（页眉页脚）
        pages = self.remove_headers_footers(pages)

        # 2. 精细化清洗每一页内容
        pages = self.clean_pages(pages)

        # 3. 汇总重建
        parsed_doc["text"] = self.rebuild_document_text(pages)
        parsed_doc["pages"] = pages

        return parsed_doc