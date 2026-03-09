from backend.services.retrieval.base_retriever import BaseRetriever
from backend.services.ranking.cross_encoder_reranker import CrossEncoderReranker


class RerankRetriever(BaseRetriever):

    def __init__(self, base_retriever):

        self.base_retriever = base_retriever
        self.reranker = CrossEncoderReranker()

    def retrieve(
        self,
        question,
        document_ids=None,
        top_k=5
    ):

        docs = self.base_retriever.retrieve(
            question,
            document_ids,
            top_k=20
        )

        docs = self.reranker.rerank(question, docs)

        return docs[:top_k]