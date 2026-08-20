from abc import ABC, abstractmethod

from app.domain.models.document import NormalizedDocument


class DocumentParser(ABC):

    @abstractmethod
    async def parse(
        self,
        file_path: str,
    ) -> NormalizedDocument:
        """Parse a document into the normalized domain representation."""
        raise NotImplementedError
