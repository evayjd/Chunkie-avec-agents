from backend.services.retrieval.vector_retriever import VectorRetriever
from backend.services.retrieval.rerank_retriever import RerankRetriever
from backend.services.retrieval.hybrid_retriever import HybridRetriever

def get_retriever(name: str, db):

    if name == "vector":
        return VectorRetriever(db)

    if name == "hybrid":
         return HybridRetriever(db)
     
    if name == "rerank":
        base = HybridRetriever(db)
        return RerankRetriever(base)
        

    raise ValueError(f"Unknown retriever: {name}")