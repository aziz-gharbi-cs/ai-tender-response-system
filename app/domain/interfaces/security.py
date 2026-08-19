from abc import ABC, abstractmethod
from typing import Any


class SecurityScanner(ABC):

    @abstractmethod
    async def scan_input(self, text: str) -> dict[str, Any]:
        """Scan input before it reaches the LLM."""
        raise NotImplementedError

    @abstractmethod
    async def scan_output(self, text: str) -> dict[str, Any]:
        """Scan generated output."""
        raise NotImplementedError
