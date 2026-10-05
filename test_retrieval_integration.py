import pytest

from app.infrastructure.vectorstore.qdrant import QdrantVectorStore
from app.rag.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from app.rag.retrieval.service import RetrievalService


@pytest.mark.asyncio
async def test_retrieval_service_with_qdrant():
    embedding_provider = SentenceTransformerEmbedding()
    vector_store = QdrantVectorStore()

    service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    results = await service.retrieve(
        "What technical documentation must the supplier provide?",
        top_k=2,
    )

    assert len(results) == 2

    first_result = results[0]

    assert first_result["score"] is not None
    assert first_result["payload"]["document_id"] == (
        "integration-document"
    )
    assert "text" in first_result["payload"]
    assert "page_number" in first_result["payload"]
