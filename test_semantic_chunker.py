from app.domain.models.document import (
    DocumentPage,
    DocumentType,
    NormalizedDocument,
)
from app.rag.chunking.semantic import SemanticChunker


def test_semantic_chunker_creates_chunks():
    document = NormalizedDocument(
        document_id="document-1",
        filename="test.pdf",
        document_type=DocumentType.PDF,
        pages=[
            DocumentPage(
                page_number=1,
                content="A" * 2500,
            )
        ],
    )

    chunker = SemanticChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk(document)

    assert len(chunks) == 3
    assert all(chunk.document_id == "document-1" for chunk in chunks)
    assert all(chunk.page_number == 1 for chunk in chunks)


def test_semantic_chunker_skips_empty_pages():
    document = NormalizedDocument(
        document_id="document-2",
        filename="test.pdf",
        document_type=DocumentType.PDF,
        pages=[
            DocumentPage(
                page_number=1,
                content="",
            ),
            DocumentPage(
                page_number=2,
                content="Hello world",
            ),
        ],
    )

    chunker = SemanticChunker()

    chunks = chunker.chunk(document)

    assert len(chunks) == 1
    assert chunks[0].page_number == 2


def test_invalid_chunk_configuration():
    try:
        SemanticChunker(
            chunk_size=100,
            chunk_overlap=100,
        )
        assert False
    except ValueError:
        assert True
