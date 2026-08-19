from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Convert text into an embedding vector."""
        raise NotImplementedError

    @abstractmethod
    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Convert multiple texts into embedding vectors."""
        raise NotImplementedError
