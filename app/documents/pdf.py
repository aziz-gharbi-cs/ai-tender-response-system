from pathlib import Path
from uuid import uuid4

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
