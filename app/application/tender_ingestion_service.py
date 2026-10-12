from typing import Any

from app.application.document_service import DocumentService
from app.domain.models.document import NormalizedDocument
from app.rag.chunking.semantic import SemanticChunker
from app.rag.ingestion.service import IngestionService


class TenderIngestionService:
    """Parse a tender document, chunk its pages, and index the chunks."""

    def __init__(
        self,
        document_service: DocumentService,
        chunker: SemanticChunker,
        ingestion_service: IngestionService,
    ) -> None:
        self.document_service = document_service
        self.chunker = chunker
        self.ingestion_service = ingestion_service

    async def ingest_document(self, file_path: str) -> NormalizedDocument:
        """Parse and index a tender, returning its normalized document."""
        document = await self.document_service.parse_document(file_path)
        chunks = self.chunker.chunk(document)

        if not chunks:
            raise ValueError(
                f"No extractable text found in document: {file_path}"
            )

        await self.ingestion_service.ingest(chunks)
        return document

    async def ingest_file(self, file_path: str) -> dict[str, Any]:
        """Parse and index a tender, returning ingestion metadata."""
        document = await self.document_service.parse_document(file_path)
        chunks = self.chunker.chunk(document)

        if not chunks:
            raise ValueError(
                f"No extractable text found in document: {file_path}"
            )

        await self.ingestion_service.ingest(chunks)

        return {
            "document_id": document.document_id,
            "filename": document.filename,
            "document_type": document.document_type.value,
            "page_count": len(document.pages),
            "chunk_count": len(chunks),
        }
