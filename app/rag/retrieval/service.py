from typing import Any

from app.domain.interfaces.embedding import EmbeddingProvider
from app.domain.interfaces.vector_store import VectorStore


class RetrievalService:

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        query_vector = await self.embedding_provider.embed_text(
            query
        )

        return await self.vector_store.similarity_search(
            query_vector,
            top_k=top_k,
        )
