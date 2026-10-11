import json
from unittest.mock import AsyncMock

import pytest

from app.agents.extraction import ExtractionAgent


@pytest.mark.asyncio
async def test_extraction_agent_parses_requirements():
    requirements = {
        "mandatory_requirements": ["Submit a technical proposal"],
        "eligibility_criteria": [],
        "technical_requirements": ["Secure API"],
        "submission_requirements": [],
        "deadlines": [],
        "evaluation_criteria": [],
        "missing_information": [],
    }
    llm = AsyncMock()
    llm.generate.return_value = json.dumps(requirements)

    agent = ExtractionAgent(llm_provider=llm)
    state = {"extracted_text": {"tender.pdf": "The proposal must include a secure API."}}

    result = await agent.run(state)

    assert result["status"] == "extracted"
    assert result["requirements"] == requirements
    llm.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_extraction_agent_rejects_invalid_json():
    llm = AsyncMock()
    llm.generate.return_value = "not valid JSON"

    agent = ExtractionAgent(llm_provider=llm)
    state = {"extracted_text": {"tender.pdf": "Tender text"}}

    result = await agent.run(state)

    assert result["status"] == "extraction_failed"
    assert any("Requirement extraction failed" in e for e in result["errors"])


@pytest.mark.asyncio
async def test_extraction_agent_rejects_missing_text():
    llm = AsyncMock()
    agent = ExtractionAgent(llm_provider=llm)

    result = await agent.run({"extracted_text": {}})

    assert result["status"] == "extraction_failed"
    llm.generate.assert_not_awaited()
