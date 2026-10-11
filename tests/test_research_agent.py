from unittest.mock import AsyncMock

import pytest

from app.agents.research import ResearchAgent


@pytest.mark.asyncio
async def test_research_agent_stores_provider_results():
    expected = {
        "findings": [
            {
                "title": "API security guidance",
                "source": "example-source",
            }
        ]
    }
    provider = AsyncMock()
    provider.research.return_value = expected

    state = {
        "requirements": {
            "technical_requirements": ["Secure API"],
        },
        "extracted_text": {"tender.pdf": "The system must expose a secure API."},
    }

    result = await ResearchAgent(provider).run(state)

    assert result["status"] == "researched"
    assert result["external_research"] == expected
    provider.research.assert_awaited_once()

    query = provider.research.await_args.args[0]
    assert "Secure API" in query
    assert "tender.pdf" in query


@pytest.mark.asyncio
async def test_research_agent_handles_provider_failure():
    provider = AsyncMock()
    provider.research.side_effect = RuntimeError("Research service unavailable")

    state = {"requirements": {"technical_requirements": ["Secure API"]}}

    result = await ResearchAgent(provider).run(state)

    assert result["status"] == "research_failed"
    assert any(
        "Research service unavailable" in error
        for error in result["errors"]
    )


@pytest.mark.asyncio
async def test_research_agent_rejects_missing_tender_information():
    provider = AsyncMock()

    result = await ResearchAgent(provider).run(
        {"requirements": {}, "extracted_text": {}}
    )

    assert result["status"] == "research_failed"
    provider.research.assert_not_awaited()


@pytest.mark.asyncio
async def test_research_agent_rejects_invalid_provider_result():
    provider = AsyncMock()
    provider.research.return_value = ["not", "a", "dictionary"]

    result = await ResearchAgent(provider).run(
        {"requirements": {"technical_requirements": ["Secure API"]}}
    )

    assert result["status"] == "research_failed"
