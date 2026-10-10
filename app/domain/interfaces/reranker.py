from abc import ABC, abstractmethod
from typing import Any


class Reranker(ABC):

    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        *,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Rank retrieved documents by their relevance to a query."""
        raise NotImplementedError
