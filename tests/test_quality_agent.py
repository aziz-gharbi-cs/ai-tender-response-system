from unittest.mock import AsyncMock

import pytest

from app.agents.quality import QualityAgent


@pytest.mark.asyncio
async def test_quality_agent_scans_source_and_proposal():
    scanner = AsyncMock()
    scanner.scan_input.return_value = {"status": "completed"}
    scanner.scan_output.return_value = {"status": "completed"}

    state = {
        "extracted_text": {"tender.pdf": "The tender requires a secure API."},
        "requirements": {"technical_requirements": ["Secure API"]},
        "proposal_draft": "Our proposal includes a secure API.",
    }

    result = await QualityAgent(scanner).run(state)

    assert result["status"] == "quality_reviewed"
    assert result["quality_report"]["findings"] == []
    scanner.scan_input.assert_awaited_once()
    scanner.scan_output.assert_awaited_once()


@pytest.mark.asyncio
async def test_quality_agent_reports_missing_proposal():
    scanner = AsyncMock()
    scanner.scan_input.return_value = {"status": "completed"}

    state = {
        "extracted_text": {"tender.pdf": "Tender content"},
        "requirements": {"mandatory_requirements": ["Technical proposal"]},
        "proposal_draft": "",
    }

    result = await QualityAgent(scanner).run(state)

    assert result["status"] == "quality_reviewed"
    assert any(
        "draft is empty" in finding
        for finding in result["quality_report"]["findings"]
    )
    scanner.scan_output.assert_not_awaited()


@pytest.mark.asyncio
async def test_quality_agent_reports_scan_failure():
    scanner = AsyncMock()
    scanner.scan_input.return_value = {"status": "completed"}
    scanner.scan_output.side_effect = RuntimeError("Scanner unavailable")

    state = {
        "extracted_text": {"tender.pdf": "Tender content"},
        "requirements": {"mandatory_requirements": ["Technical proposal"]},
        "proposal_draft": "A proposal draft.",
    }

    result = await QualityAgent(scanner).run(state)

    assert result["status"] == "quality_review_failed"
    assert any(
        "Scanner unavailable" in error
        for error in result["quality_report"]["scan_errors"]
    )
