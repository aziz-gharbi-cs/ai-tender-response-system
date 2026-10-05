import pytest

from app.domain.models.chunk import DocumentChunk
from app.infrastructure.vectorstore.qdrant import QdrantVectorStore
from app.rag.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from app.rag.ingestion.service import IngestionService


@pytest.mark.asyncio
async def test_qdrant_ingestion_and_search():
    embedding_provider = SentenceTransformerEmbedding()
    vector_store = QdrantVectorStore()

    service = IngestionService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    chunks = [
        DocumentChunk(
            chunk_id="integration-chunk-1",
            document_id="integration-document",
            text=(
                "The supplier must provide technical "
                "documentation for the proposed system."
            ),
            page_number=10,
            chunk_index=0,
        ),
        DocumentChunk(
            chunk_id="integration-chunk-2",
            document_id="integration-document",
            text=(
                "The supplier must submit financial "
                "statements for the last three years."
            ),
            page_number=11,
            chunk_index=1,
        ),
    ]

    await service.ingest(chunks)

    query = (
        "What technical documentation must the supplier provide?"
    )

    query_vector = await embedding_provider.embed_text(query)

    results = await vector_store.similarity_search(
        query_vector,
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["payload"]["document_id"] == (
        "integration-document"
    )
    assert results[0]["payload"]["page_number"] in (10, 11)
