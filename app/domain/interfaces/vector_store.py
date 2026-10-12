from abc import ABC, abstractmethod
from typing import Any


class VectorStore(ABC):

    @abstractmethod
    async def add_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
        """
        Store vectorized document chunks.

        Each document should contain:
        - id
        - vector
        - payload
        """
        raise NotImplementedError

    @abstractmethod
    async def similarity_search(
        self,
        query_vector: list[float],
        *,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return relevant documents, optionally restricted to one document."""
        raise NotImplementedError
