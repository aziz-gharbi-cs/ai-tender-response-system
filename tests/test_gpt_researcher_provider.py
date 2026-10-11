from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.research.gpt_researcher import GPTResearcherProvider


@pytest.mark.asyncio
async def test_provider_returns_report_and_sources():
    researcher = MagicMock()
    researcher.conduct_research = AsyncMock(return_value=None)
    researcher.write_report = AsyncMock(return_value="Research findings")
    researcher.get_research_sources.return_value = ["Source A"]
    researcher.get_source_urls.return_value = ["https://example.com"]

    with patch(
        "app.research.gpt_researcher.GPTResearcher",
        return_value=researcher,
    ):
        result = await GPTResearcherProvider().research("Research secure APIs")

    assert result["report"] == "Research findings"
    assert result["sources"] == ["Source A"]
    assert result["source_urls"] == ["https://example.com"]
    researcher.conduct_research.assert_awaited_once()
    researcher.write_report.assert_awaited_once()


@pytest.mark.asyncio
async def test_provider_rejects_empty_query():
    with pytest.raises(ValueError, match="Research query cannot be empty"):
        await GPTResearcherProvider().research("   ")
