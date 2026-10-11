from unittest.mock import AsyncMock

import pytest

from app.application.container import ApplicationContainer
from app.graph.workflow import build_proposal_workflow


@pytest.mark.asyncio
async def test_workflow_runs_all_nodes_in_order():
    llm = AsyncMock()
    llm.generate.return_value = "Technical proposal draft"

    retriever = AsyncMock()
    retriever.retrieve.return_value = [
        {
            "payload": {
                "text": "The system must provide a secure API.",
                "source": "technical-spec.pdf",
                "page": 2,
            },
            "rerank_score": 0.95,
        }
    ]

    research = AsyncMock()
    research.research.return_value = {
        "findings": ["Relevant technical background"]
    }

    scanner = AsyncMock()
    scanner.scan_input.return_value = {"findings": []}
    scanner.scan_output.return_value = {"findings": []}

    container = ApplicationContainer(
        research_provider=research,
        llm_provider=llm,
        retriever=retriever,
        security_scanner=scanner,
    )

    workflow = build_proposal_workflow(container)

    result = await workflow.ainvoke(
        {
            "request_id": "workflow-test",
            "input_documents": ["technical-spec.pdf"],
            "extracted_text": {
                "technical-spec.pdf": (
                    "The system must provide a secure API."
                )
            },
            "requirements": {
                "technical_requirements": ["Secure API"]
            },
            "errors": [],
        }
    )

    assert result["status"] == "quality_reviewed"
    assert result["proposal_draft"] == "Technical proposal draft"
    assert result["external_research"] == {
        "findings": ["Relevant technical background"]
    }
    assert result["quality_report"]["proposal_present"] is True

    research.research.assert_awaited_once()
    retriever.retrieve.assert_awaited_once()
    llm.generate.assert_awaited_once()
    scanner.scan_input.assert_awaited_once()
    scanner.scan_output.assert_awaited_once()


@pytest.mark.asyncio
async def test_workflow_stops_at_verifier_without_documents():
    container = ApplicationContainer(
        research_provider=AsyncMock(),
        llm_provider=AsyncMock(),
        retriever=AsyncMock(),
        security_scanner=AsyncMock(),
    )

    workflow = build_proposal_workflow(container)
    result = await workflow.ainvoke(
        {
            "input_documents": [],
            "errors": [],
        }
    )

    assert result["status"] == "verification_failed"
    assert "No input documents were provided." in result["errors"]
