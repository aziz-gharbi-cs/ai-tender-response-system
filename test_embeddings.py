import pytest

from app.rag.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)


@pytest.mark.asyncio
async def test_embed_text():
    provider = SentenceTransformerEmbedding()

    vector = await provider.embed_text(
        "The supplier must provide technical documentation."
    )

    assert len(vector) == 384
    assert all(isinstance(value, float) for value in vector)


@pytest.mark.asyncio
async def test_embed_documents():
    provider = SentenceTransformerEmbedding()

    vectors = await provider.embed_documents(
        [
            "Technical requirements.",
            "Financial requirements.",
        ]
    )

    assert len(vectors) == 2
    assert all(len(vector) == 384 for vector in vectors)
