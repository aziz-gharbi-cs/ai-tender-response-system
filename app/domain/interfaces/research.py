from abc import ABC, abstractmethod
from typing import Any


class ResearchProvider(ABC):

    @abstractmethod
    async def research(self, query: str) -> dict[str, Any]:
        """Perform external research and return structured results."""
        raise NotImplementedError
