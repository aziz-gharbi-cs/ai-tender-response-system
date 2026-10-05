from typing import Any

from app.domain.interfaces.embedding import EmbeddingProvider
from app.domain.interfaces.vector_store import VectorStore
from app.domain.models.chunk import DocumentChunk


class IngestionService:

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def ingest(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]

        vectors = await self.embedding_provider.embed_documents(texts)

        if len(vectors) != len(chunks):
            raise ValueError(
                "Number of embeddings must match number of chunks."
            )

        documents: list[dict[str, Any]] = []

        for chunk, vector in zip(chunks, vectors):
            payload: dict[str, Any] = {
                "document_id": chunk.document_id,
                "text": chunk.text,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
            }

            payload.update(chunk.metadata)

            documents.append(
                {
                    "id": chunk.chunk_id,
                    "vector": vector,
                    "payload": payload,
                }
            )

        await self.vector_store.add_documents(documents)
