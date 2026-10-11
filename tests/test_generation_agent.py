from unittest.mock import AsyncMock

import pytest

from app.agents.generation import GenerationAgent


@pytest.mark.asyncio
async def test_generation_agent_creates_proposal():
    llm = AsyncMock()
    llm.generate.return_value = "Technical Proposal\n\nOur approach..."

    retriever = AsyncMock()
    retriever.retrieve.return_value = [
        {
            "payload": {
                "text": "The project requires a secure API.",
                "source": "requirements.pdf",
                "page": 2,
            },
            "rerank_score": 0.95,
        }
    ]

    state = {
        "requirements": {"security": "Secure API"},
        "extracted_text": {},
        "errors": [],
    }

    agent = GenerationAgent(llm_provider=llm, retriever=retriever)
    result = await agent.run(state)

    assert result["status"] == "generated"
    assert result["proposal_draft"] == "Technical Proposal\n\nOur approach..."
    retriever.retrieve.assert_awaited_once()
    llm.generate.assert_awaited_once()

    prompt = llm.generate.await_args.kwargs["system_prompt"]
    assert "Never invent" in prompt


@pytest.mark.asyncio
async def test_generation_agent_handles_retrieval_failure():
    llm = AsyncMock()
    retriever = AsyncMock()
    retriever.retrieve.side_effect = RuntimeError("Qdrant unavailable")

    state = {"requirements": {}, "errors": []}
    agent = GenerationAgent(llm_provider=llm, retriever=retriever)

    result = await agent.run(state)

    assert result["status"] == "generation_failed"
    assert any("Qdrant unavailable" in error for error in result["errors"])
    llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_generation_agent_handles_empty_llm_response():
    llm = AsyncMock()
    llm.generate.return_value = "   "

    retriever = AsyncMock()
    retriever.retrieve.return_value = []

    state = {"requirements": {}, "errors": []}
    agent = GenerationAgent(llm_provider=llm, retriever=retriever)

    result = await agent.run(state)

    assert result["status"] == "generation_failed"
    assert any("empty proposal draft" in error for error in result["errors"])
