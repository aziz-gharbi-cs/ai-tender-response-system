from abc import ABC, abstractmethod
from typing import Any


class VectorStore(ABC):

    @abstractmethod
    async def add_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
        """Store documents/chunks in the vector database."""
        raise NotImplementedError

    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        *,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Return the most relevant documents for a query."""
        raise NotImplementedError
