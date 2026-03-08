from typing import List, Dict


class CitationBuilder:
    """
    CitationBuilder 负责：

    1. 为检索结果生成稳定的 citation_id
    2. 去重（相同 chunk 不重复引用）
    3. 生成 snippet（用于前端展示）
    4. 输出统一 citation 结构
    """

    def __init__(self, snippet_length: int = 200):
        # snippet最大长度
        self.snippet_length = snippet_length

    # --------------------------------------------------
    # snippet生成
    # --------------------------------------------------

    def build_snippet(self, text: str) -> str:
        """
        从chunk文本生成snippet
        """

        if not text:
            return ""

        text = text.strip()

        if len(text) <= self.snippet_length:
            return text

        return text[: self.snippet_length] + "..."

    # --------------------------------------------------
    # 去重
    # --------------------------------------------------

    def deduplicate_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        防止相同chunk被重复引用
        """

        seen = set()
        results = []

        for chunk in chunks:

            key = chunk["chunk_id"]

            if key in seen:
                continue

            seen.add(key)

            results.append(chunk)

        return results

    # --------------------------------------------------
    # 生成citation列表
    # --------------------------------------------------

    def build_citations(self, chunks: List[Dict]) -> List[Dict]:
        """
        输入：retriever返回的chunks
        输出：标准citation格式
        """

        chunks = self.deduplicate_chunks(chunks)

        citations = []

        for i, chunk in enumerate(chunks):

            snippet = self.build_snippet(chunk["content"])

            citation = {
                "citation_id": i + 1,
                "doc_id": chunk["doc_id"],
                "chunk_id": chunk["chunk_id"],
                "chunk_index": chunk["chunk_index"],
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
                "section": chunk.get("section"),
                "snippet": snippet
            }

            citations.append(citation)

        return citations