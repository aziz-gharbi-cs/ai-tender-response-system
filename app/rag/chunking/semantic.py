from uuid import uuid4

from app.domain.models.chunk import DocumentChunk
from app.domain.models.document import NormalizedDocument


class SemanticChunker:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(
        self,
        document: NormalizedDocument,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for page in document.pages:
            text = page.content.strip()

            if not text:
                continue

            start = 0

            while start < len(text):
                end = min(
                    start + self.chunk_size,
                    len(text),
                )

                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=str(uuid4()),
                            document_id=document.document_id,
                            text=chunk_text,
                            page_number=page.page_number,
                            chunk_index=chunk_index,
                        )
                    )

                    chunk_index += 1

                if end >= len(text):
                    break

                start = end - self.chunk_overlap

        return chunks
