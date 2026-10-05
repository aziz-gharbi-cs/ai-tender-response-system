import pytest

from app.rag.retrieval.service import RetrievalService


class FakeEmbeddingProvider:

    async def embed_text(
        self,
        text: str,
    ) -> list[float]:
        return [1.0, 2.0, 3.0]


class FakeVectorStore:

    def __init__(self) -> None:
        self.query_vector = None
        self.top_k = None

    async def similarity_search(
        self,
        query_vector: list[float],
        *,
        top_k: int = 5,
    ) -> list[dict]:
        self.query_vector = query_vector
        self.top_k = top_k

        return [
            {
                "id": "chunk-1",
                "score": 0.95,
                "payload": {
                    "text": "Technical requirements.",
                    "page_number": 4,
                },
            }
        ]


@pytest.mark.asyncio
async def test_retrieval_service():
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()

    service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    results = await service.retrieve(
        "What are the technical requirements?",
        top_k=3,
    )

    assert len(results) == 1
    assert results[0]["id"] == "chunk-1"
    assert results[0]["payload"]["page_number"] == 4

    assert vector_store.query_vector == [1.0, 2.0, 3.0]
    assert vector_store.top_k == 3


@pytest.mark.asyncio
async def test_empty_query_is_rejected():
    service = RetrievalService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=FakeVectorStore(),
    )

    with pytest.raises(ValueError):
        await service.retrieve("   ")


@pytest.mark.asyncio
async def test_invalid_top_k_is_rejected():
    service = RetrievalService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=FakeVectorStore(),
    )

    with pytest.raises(ValueError):
        await service.retrieve(
            "technical requirements",
            top_k=0,
        )
