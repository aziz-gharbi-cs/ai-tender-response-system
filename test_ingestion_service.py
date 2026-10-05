import pytest

from app.domain.models.chunk import DocumentChunk
from app.rag.ingestion.service import IngestionService


class FakeEmbeddingProvider:

    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            [float(index), 0.5, 1.0]
            for index, _ in enumerate(texts)
        ]


class FakeVectorStore:

    def __init__(self) -> None:
        self.documents = []

    async def add_documents(
        self,
        documents: list[dict],
    ) -> None:
        self.documents = documents


@pytest.mark.asyncio
async def test_ingestion_service():
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()

    service = IngestionService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    chunks = [
        DocumentChunk(
            chunk_id="chunk-1",
            document_id="document-1",
            text="Technical requirements.",
            page_number=4,
            chunk_index=0,
        ),
        DocumentChunk(
            chunk_id="chunk-2",
            document_id="document-1",
            text="Financial requirements.",
            page_number=5,
            chunk_index=1,
        ),
    ]

    await service.ingest(chunks)

    assert len(vector_store.documents) == 2

    assert vector_store.documents[0]["id"] == "chunk-1"
    assert vector_store.documents[0]["vector"] == [0.0, 0.5, 1.0]

    assert vector_store.documents[0]["payload"]["text"] == (
        "Technical requirements."
    )

    assert vector_store.documents[0]["payload"]["page_number"] == 4
