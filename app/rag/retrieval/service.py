from typing import Any

from app.domain.interfaces.embedding import EmbeddingProvider
from app.domain.interfaces.reranker import Reranker
from app.domain.interfaces.vector_store import VectorStore


class RetrievalService:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        reranker: Reranker | None = None,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.reranker = reranker

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        candidate_k: int | None = None,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        if candidate_k is None:
            candidate_k = max(top_k * 4, top_k) if self.reranker else top_k

        if candidate_k < top_k:
            raise ValueError("candidate_k must be greater than or equal to top_k.")

        query_vector = await self.embedding_provider.embed_text(query)

        documents = await self.vector_store.similarity_search(
            query_vector,
            top_k=candidate_k if self.reranker else top_k,
        )

        if self.reranker is not None:
            documents = await self.reranker.rerank(
                query,
                documents,
                top_k=top_k,
            )

        return documents
