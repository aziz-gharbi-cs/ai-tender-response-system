from pathlib import Path
from uuid import uuid4

import camelot
import pdfplumber

from app.domain.interfaces.document_parser import DocumentParser
from app.domain.models.document import (
    DocumentPage,
    DocumentType,
    NormalizedDocument,
)


class PDFParser(DocumentParser):

    async def parse(
        self,
        file_path: str,
    ) -> NormalizedDocument:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {path.suffix}"
            )

        pages: list[DocumentPage] = []

        with pdfplumber.open(path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""

                pages.append(
                    DocumentPage(
                        page_number=page_number,
                        content=text,
                    )
                )

        self._extract_tables(path, pages)

        return NormalizedDocument(
            document_id=str(uuid4()),
            filename=path.name,
            document_type=DocumentType.PDF,
            pages=pages,
            metadata={
                "page_count": len(pages),
                "source_path": str(path),
            },
        )

    @staticmethod
    def _extract_tables(
        path: Path,
        pages: list[DocumentPage],
    ) -> None:
        try:
            tables = camelot.read_pdf(
                str(path),
                pages="all",
                flavor="stream",
            )
        except Exception:  # noqa: BLE001
            return

        for table in tables:
            page_number = int(table.page)

            if page_number < 1 or page_number > len(pages):
                continue

            rows = [
                [
                    cell.strip()
                    for cell in row
                ]
                for row in table.data
            ]

            rows = [
                row
                for row in rows
                if any(cell for cell in row)
            ]

            if not rows:
                continue

            pages[page_number - 1].metadata.setdefault(
                "tables",
                [],
            ).append(
                {
                    "rows": rows,
                }
            )
