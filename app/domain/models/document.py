from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    SCANNED = "scanned"
    UNKNOWN = "unknown"


@dataclass
class DocumentPage:
    page_number: int
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedDocument:
    document_id: str
    filename: str
    document_type: DocumentType
    pages: list[DocumentPage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return "\n\n".join(
            page.content
            for page in self.pages
            if page.content.strip()
        )
