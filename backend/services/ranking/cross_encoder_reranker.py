from sentence_transformers import CrossEncoder


class CrossEncoderReranker:

    def __init__(self):

        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(self, question, docs):

        pairs = [
            (question, d["content"])
            for d in docs
        ]

        scores = self.model.predict(pairs)

        for doc, score in zip(docs, scores):
            doc["rerank_score"] = float(score)

        docs.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return docs