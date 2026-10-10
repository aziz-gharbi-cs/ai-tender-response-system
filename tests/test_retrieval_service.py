import pytest

from app.rag.retrieval.service import RetrievalService


class FakeEmbeddingProvider:
    async def embed_text(self, text: str) -> list[float]:
        return [0.1, 0.2]

    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [[0.1, 0.2] for _ in texts]


class FakeVectorStore:
    def __init__(self) -> None:
        self.requested_top_k: int | None = None

    async def similarity_search(
        self,
        query_vector: list[float],
        *,
        top_k: int = 5,
    ) -> list[dict]:
        self.requested_top_k = top_k
        return [
            {"id": str(i), "payload": {"text": f"Chunk {i}"}}
            for i in range(top_k)
        ]

    async def add_documents(self, documents: list[dict]) -> None:
        pass


class FakeReranker:
    async def rerank(
        self,
        query: str,
        documents: list[dict],
        *,
        top_k: int = 5,
    ) -> list[dict]:
        return [
            {**document, "rerank_score": float(len(documents) - i)}
            for i, document in enumerate(documents[:top_k])
        ]


@pytest.mark.asyncio
async def test_retrieval_without_reranker_uses_top_k() -> None:
    store = FakeVectorStore()
    service = RetrievalService(FakeEmbeddingProvider(), store)

    results = await service.retrieve("technical documentation", top_k=3)

    assert store.requested_top_k == 3
    assert len(results) == 3
    assert "rerank_score" not in results[0]


@pytest.mark.asyncio
async def test_retrieval_uses_more_candidates_when_reranking() -> None:
    store = FakeVectorStore()
    service = RetrievalService(
        FakeEmbeddingProvider(),
        store,
        FakeReranker(),
    )

    results = await service.retrieve("technical documentation", top_k=3)

    assert store.requested_top_k == 12
    assert len(results) == 3
    assert results[0]["rerank_score"] > results[1]["rerank_score"]


@pytest.mark.asyncio
async def test_retrieval_accepts_explicit_candidate_k() -> None:
    store = FakeVectorStore()
    service = RetrievalService(
        FakeEmbeddingProvider(),
        store,
        FakeReranker(),
    )

    await service.retrieve(
        "technical documentation",
        top_k=3,
        candidate_k=8,
    )

    assert store.requested_top_k == 8


@pytest.mark.asyncio
async def test_retrieval_rejects_candidate_k_smaller_than_top_k() -> None:
    service = RetrievalService(
        FakeEmbeddingProvider(),
        FakeVectorStore(),
        FakeReranker(),
    )

    with pytest.raises(ValueError, match="candidate_k"):
        await service.retrieve(
            "technical documentation",
            top_k=5,
            candidate_k=3,
        )


@pytest.mark.asyncio
async def test_retrieval_rejects_empty_query() -> None:
    service = RetrievalService(FakeEmbeddingProvider(), FakeVectorStore())

    with pytest.raises(ValueError, match="Query cannot be empty"):
        await service.retrieve("   ")
