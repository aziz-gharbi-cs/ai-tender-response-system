from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    text: str
    page_number: int
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)
