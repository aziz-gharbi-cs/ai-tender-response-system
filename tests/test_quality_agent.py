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

@pytest.mark.asyncio
async def test_quality_agent_evaluates_proposal_with_llm_judge():
    scanner = AsyncMock()
    scanner.scan_input.return_value = {"status": "completed"}
    scanner.scan_output.return_value = {"status": "completed"}

    llm = AsyncMock()
    llm.generate.return_value = """{
        "score": 85,
        "strengths": ["Addresses the secure API requirement"],
        "weaknesses": ["Implementation details could be clearer"],
        "missing_requirements": [],
        "assessment": "A strong proposal that meets the supplied requirements."
    }"""

    state = {
        "extracted_text": {"tender.pdf": "The tender requires a secure API."},
        "requirements": {"technical_requirements": ["Secure API"]},
        "proposal_draft": "Our proposal includes a secure API.",
    }

    result = await QualityAgent(
        scanner, llm_provider=llm
    ).run(state)

    report = result["quality_report"]
    judge = report["judge_evaluation"]

    assert result["status"] == "quality_reviewed"
    assert judge["status"] == "completed"
    assert judge["score"] == 85
    assert "Addresses the secure API requirement" in judge["strengths"]
    assert judge["missing_requirements"] == []
    llm.generate.assert_awaited_once()
    scanner.scan_input.assert_awaited_once()
    scanner.scan_output.assert_awaited_once()


@pytest.mark.asyncio
async def test_quality_agent_handles_judge_failure():
    scanner = AsyncMock()
    scanner.scan_input.return_value = {"status": "completed"}
    scanner.scan_output.return_value = {"status": "completed"}

    llm = AsyncMock()
    llm.generate.side_effect = RuntimeError("Judge unavailable")

    state = {
        "extracted_text": {"tender.pdf": "Tender content"},
        "requirements": {"mandatory_requirements": ["Technical proposal"]},
        "proposal_draft": "A proposal draft.",
    }

    result = await QualityAgent(
        scanner, llm_provider=llm
    ).run(state)

    assert result["status"] == "quality_reviewed"
    assert result["quality_report"]["judge_evaluation"]["status"] == "failed"
    assert "Judge unavailable" in result["quality_report"]["judge_evaluation"]["error"]
    scanner.scan_input.assert_awaited_once()
    scanner.scan_output.assert_awaited_once()
