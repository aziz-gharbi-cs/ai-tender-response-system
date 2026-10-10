import json

import httpx
import pytest

from app.llm.provider import OllamaLLMProvider


@pytest.fixture
def mock_ollama(monkeypatch):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": "Generated proposal text",
                }
            },
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        return original_client(
            *args,
            transport=transport,
            **kwargs,
        )

    monkeypatch.setattr(
        "app.llm.provider.httpx.AsyncClient",
        client_factory,
    )
    return requests


@pytest.mark.asyncio
async def test_generate_returns_model_response(mock_ollama):
    provider = OllamaLLMProvider()

    result = await provider.generate("Draft a proposal")

    assert result == "Generated proposal text"
    assert len(mock_ollama) == 1


@pytest.mark.asyncio
async def test_generate_sends_model_and_system_prompt(mock_ollama):
    provider = OllamaLLMProvider(model="qwen2.5:7b")

    await provider.generate(
        "Draft a proposal",
        system_prompt="You are a procurement assistant.",
    )

    request = mock_ollama[0]
    payload = json.loads(request.content)

    assert request.url.path == "/api/chat"
    assert payload["model"] == "qwen2.5:7b"
    assert payload["stream"] is False
    assert payload["messages"] == [
        {
            "role": "system",
            "content": "You are a procurement assistant.",
        },
        {
            "role": "user",
            "content": "Draft a proposal",
        },
    ]


@pytest.mark.asyncio
async def test_empty_prompt_is_rejected():
    provider = OllamaLLMProvider()

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        await provider.generate("   ")


@pytest.mark.asyncio
async def test_http_error_is_propagated(monkeypatch):
    def handler(request):
        return httpx.Response(500, request=request)

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        return original_client(
            *args,
            transport=transport,
            **kwargs,
        )

    monkeypatch.setattr(
        "app.llm.provider.httpx.AsyncClient",
        client_factory,
    )

    provider = OllamaLLMProvider()

    with pytest.raises(httpx.HTTPStatusError):
        await provider.generate("Draft a proposal")


@pytest.mark.asyncio
async def test_empty_model_response_is_rejected(monkeypatch):
    def handler(request):
        return httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": ""}},
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        return original_client(
            *args,
            transport=transport,
            **kwargs,
        )

    monkeypatch.setattr(
        "app.llm.provider.httpx.AsyncClient",
        client_factory,
    )

    provider = OllamaLLMProvider()

    with pytest.raises(RuntimeError, match="empty response"):
        await provider.generate("Draft a proposal")
