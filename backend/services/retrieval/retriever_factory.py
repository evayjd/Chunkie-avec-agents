from backend.services.retrieval.vector_retriever import VectorRetriever

from backend.services.retrieval.hybrid_retriever import HybridRetriever

def get_retriever(name: str, db):

    if name == "vector":
        return VectorRetriever(db)

    if name == "hybrid":
         return HybridRetriever(db)

    raise ValueError(f"Unknown retriever: {name}")