from sentence_transformers import SentenceTransformer

from app.domain.interfaces.embedding import EmbeddingProvider


class SentenceTransformerEmbedding(EmbeddingProvider):

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.model = SentenceTransformer(model_name)

    async def embed_text(
        self,
        text: str,
    ) -> list[float]:
        vector = self.model.encode(
            text,
            convert_to_numpy=True,
        )

        return vector.tolist()

    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
        )

        return vectors.tolist()
