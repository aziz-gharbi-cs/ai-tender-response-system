import pytest

from app.documents.pdf import PDFParser


@pytest.mark.asyncio
async def test_pdf_parser():
    document = await PDFParser().parse("test_document.pdf")

    assert document.filename == "test_document.pdf"
    assert len(document.pages) > 0
    assert document.full_text is not None
