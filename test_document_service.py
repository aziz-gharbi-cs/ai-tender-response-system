import pytest

from app.application.document_service import DocumentService
from app.domain.models.document import DocumentType


@pytest.mark.asyncio
async def test_document_service_parses_pdf():
    service = DocumentService()

    document = await service.parse_document("test_document.pdf")

    assert document.filename == "test_document.pdf"
    assert document.document_type == DocumentType.PDF
    assert len(document.pages) > 0
