import httpx

from app.domain.interfaces.llm import LLMProvider


class OllamaLLMProvider(LLMProvider):
    """Generate text using a local Ollama model."""

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        base_url: str = "http://localhost:11434",
        timeout: float = 180.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        messages.append({
            "role": "user",
            "content": prompt,
        })

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()

        content = data.get("message", {}).get("content")
        if not content:
            raise RuntimeError("Ollama returned an empty response.")

        return content
