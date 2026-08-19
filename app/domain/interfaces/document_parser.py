from abc import ABC, abstractmethod


class DocumentParser(ABC):

    @abstractmethod
    async def extract_text(self, file_path: str) -> str:
        """Extract normalized text from a document."""
        raise NotImplementedError
