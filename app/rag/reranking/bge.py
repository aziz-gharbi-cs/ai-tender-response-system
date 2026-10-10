from typing import Any

from sentence_transformers import CrossEncoder

from app.domain.interfaces.reranker import Reranker


class BGEReranker(Reranker):
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        device: str = "cpu",
    ) -> None:
        self.model = CrossEncoder(model_name, device=device)

    async def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        *,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        if not documents:
            return []

        pairs = [
            [query, document["payload"]["text"]]
            for document in documents
        ]

        scores = self.model.predict(pairs)

        ranked_documents = [
            {**document, "rerank_score": float(score)}
            for document, score in zip(documents, scores, strict=True)
        ]

        ranked_documents.sort(
            key=lambda document: document["rerank_score"],
            reverse=True,
        )

        return ranked_documents[:top_k]
