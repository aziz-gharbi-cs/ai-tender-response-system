import asyncio

import pytest

from app.rag.reranking.bge import BGEReranker


class FakeCrossEncoder:
    def predict(self, pairs):
        return [0.2, 0.9, 0.5][:len(pairs)]


def make_reranker():
    reranker = BGEReranker.__new__(BGEReranker)
    reranker.model = FakeCrossEncoder()
    return reranker


def make_documents():
    return [
        {"id": "1", "payload": {"text": "Document A"}},
        {"id": "2", "payload": {"text": "Document B"}},
        {"id": "3", "payload": {"text": "Document C"}},
    ]


def test_reranker_sorts_documents_by_score():
    reranker = make_reranker()

    results = asyncio.run(
        reranker.rerank("test query", make_documents())
    )

    assert [doc["id"] for doc in results] == ["2", "3", "1"]
    assert [doc["rerank_score"] for doc in results] == [0.9, 0.5, 0.2]


def test_reranker_preserves_original_document_data():
    reranker = make_reranker()
    documents = make_documents()

    results = asyncio.run(
        reranker.rerank("test query", documents)
    )

    best_document = results[0]
    assert best_document["payload"]["text"] == "Document B"
    assert best_document["id"] == "2"
    assert best_document["rerank_score"] == 0.9


def test_reranker_limits_results_to_top_k():
    reranker = make_reranker()

    results = asyncio.run(
        reranker.rerank("test query", make_documents(), top_k=2)
    )

    assert len(results) == 2
    assert [doc["id"] for doc in results] == ["2", "3"]


def test_reranker_returns_empty_list_for_no_documents():
    reranker = make_reranker()

    results = asyncio.run(
        reranker.rerank("test query", [])
    )

    assert results == []


def test_reranker_rejects_empty_query():
    reranker = make_reranker()

    with pytest.raises(ValueError, match="Query cannot be empty"):
        asyncio.run(reranker.rerank("   ", make_documents()))


def test_reranker_rejects_invalid_top_k():
    reranker = make_reranker()

    with pytest.raises(ValueError, match="top_k must be greater than 0"):
        asyncio.run(
            reranker.rerank("test query", make_documents(), top_k=0)
        )
