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
    assert llm.generate.await_count == 2
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


@pytest.mark.asyncio
async def test_workflow_ingests_real_pdf_before_generating_proposal():
    from pathlib import Path
    from unittest.mock import AsyncMock, Mock

    from app.application.document_service import DocumentService
    from app.application.tender_ingestion_service import TenderIngestionService
    from app.rag.chunking.semantic import SemanticChunker
    from app.rag.ingestion.service import IngestionService

    pdf_path = Path(__file__).resolve().parents[1] / "test_document.pdf"
    assert pdf_path.is_file(), f"Test PDF not found: {pdf_path}"

    vector_store = Mock()
    vector_store.add_documents = AsyncMock()

    embedding_provider = Mock()
    embedding_provider.embed_documents = AsyncMock(
        side_effect=lambda texts: [[0.1, 0.2, 0.3] for _ in texts]
    )

    tender_ingestion = TenderIngestionService(
        document_service=DocumentService(),
        chunker=SemanticChunker(),
        ingestion_service=IngestionService(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        ),
    )

    llm = AsyncMock()
    llm.generate.return_value = "Technical proposal generated from the PDF."

    retriever = AsyncMock()
    retriever.retrieve.return_value = [
        {
            "payload": {
                "text": "The tender requires PDF processing and proposal generation.",
                "source": "test_document.pdf",
                "page": 1,
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
        ingestion_service=tender_ingestion,
    )

    workflow = build_proposal_workflow(container)
    result = await workflow.ainvoke(
        {
            "request_id": "real-pdf-ingestion-test",
            "input_documents": [str(pdf_path)],
            "errors": [],
        }
    )

    assert result["status"] == "quality_reviewed"
    assert result["document_id"]
    assert result["extracted_text"]

    extracted_text = "\n".join(result["extracted_text"].values())
    assert "AI Tender Response System" in extracted_text

    embedding_provider.embed_documents.assert_awaited_once()
    vector_store.add_documents.assert_awaited_once()

    indexed_documents = vector_store.add_documents.await_args.args[0]
    assert indexed_documents
    assert all(
        item["payload"]["document_id"] == result["document_id"]
        for item in indexed_documents
    )

    retriever.retrieve.assert_awaited_once()
    assert llm.generate.await_count == 2
    assert result["proposal_draft"] == (
        "Technical proposal generated from the PDF."
    )
    assert result["quality_report"]["proposal_present"] is True
