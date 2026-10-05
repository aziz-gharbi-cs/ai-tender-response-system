import pytest

from app.documents.pdf import PDFParser


@pytest.mark.asyncio
async def test_table_parser():
    document = await PDFParser().parse("test_table.pdf")

    assert document.filename == "test_table.pdf"
    assert len(document.pages) > 0

    tables = []

    for page in document.pages:
        tables.extend(page.metadata.get("tables", []))

    assert len(tables) > 0
