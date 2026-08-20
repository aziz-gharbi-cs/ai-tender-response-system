from pathlib import Path

from app.documents.docx import DOCXParser
from app.documents.pdf import PDFParser
from app.domain.interfaces.document_parser import DocumentParser


class DocumentFactory:

    @staticmethod
    def create(file_path: str) -> DocumentParser:
        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return PDFParser()

        if extension == ".docx":
            return DOCXParser()

        raise ValueError(
            f"Unsupported document format: {extension}"
        )
