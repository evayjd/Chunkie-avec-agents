from abc import ABC, abstractmethod
from typing import List, Dict


class BaseRetriever(ABC):
    """
    所有 retriever 的统一接口
    """

    @abstractmethod
    def retrieve(
        self,
        question: str,
        document_ids: List[str] | None = None,
        top_k: int = 5
    ) -> List[Dict]:
        pass