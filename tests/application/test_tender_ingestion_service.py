from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.tender_ingestion_service import TenderIngestionService
from app.domain.models.document import DocumentType, NormalizedDocument
from app.domain.models.chunk import DocumentChunk


@pytest.fixture
def dependencies():
    document_service = MagicMock()
    document_service.parse_document = AsyncMock()
    chunker = MagicMock()
    ingestion_service = MagicMock()
    ingestion_service.ingest = AsyncMock()

    service = TenderIngestionService(
        document_service=document_service,
        chunker=chunker,
        ingestion_service=ingestion_service,
    )
    return service, document_service, chunker, ingestion_service


@pytest.mark.asyncio
async def test_ingest_file_success(dependencies):
    service, document_service, chunker, ingestion_service = dependencies

    document = NormalizedDocument(
        document_id="doc-123",
        filename="tender.pdf",
        document_type=DocumentType.PDF,
        pages=[],
    )
    chunks = [
        DocumentChunk(
            chunk_id="chunk-1",
            document_id="doc-123",
            text="Tender requirements",
            page_number=1,
            chunk_index=0,
        )
    ]

    document_service.parse_document.return_value = document
    chunker.chunk.return_value = chunks

    result = await service.ingest_file("tender.pdf")

    document_service.parse_document.assert_awaited_once_with("tender.pdf")
    chunker.chunk.assert_called_once_with(document)
    ingestion_service.ingest.assert_awaited_once_with(chunks)

    assert result == {
        "document_id": "doc-123",
        "filename": "tender.pdf",
        "document_type": "pdf",
        "page_count": 0,
        "chunk_count": 1,
    }


@pytest.mark.asyncio
async def test_ingest_file_rejects_empty_chunks(dependencies):
    service, document_service, chunker, ingestion_service = dependencies

    document = NormalizedDocument(
        document_id="doc-123",
        filename="empty.pdf",
        document_type=DocumentType.PDF,
        pages=[],
    )
    document_service.parse_document.return_value = document
    chunker.chunk.return_value = []

    with pytest.raises(ValueError, match="No extractable text"):
        await service.ingest_file("empty.pdf")

    ingestion_service.ingest.assert_not_awaited()



@pytest.mark.asyncio
async def test_ingest_document_returns_normalized_document():
    from unittest.mock import AsyncMock, Mock

    document_service = Mock()
    document = Mock()
    document.document_id = "doc-123"
    document.filename = "tender.pdf"
    document_service.parse_document = AsyncMock(return_value=document)

    chunker = Mock()
    chunks = [{"text": "Tender requirement"}]
    chunker.chunk.return_value = chunks

    ingestion_service = Mock()
    ingestion_service.ingest = AsyncMock()

    service = TenderIngestionService(
        document_service=document_service,
        chunker=chunker,
        ingestion_service=ingestion_service,
    )

    result = await service.ingest_document("tender.pdf")

    assert result is document
    document_service.parse_document.assert_awaited_once_with("tender.pdf")
    chunker.chunk.assert_called_once_with(document)
    ingestion_service.ingest.assert_awaited_once_with(chunks)
