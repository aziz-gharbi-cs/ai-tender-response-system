from collections.abc import Callable

from app.agents.base import BaseAgent
from app.agents.extraction import ExtractionAgent
from app.agents.verifier import VerifierAgent
from app.graph.state import ProposalState


async def verifier_node(state: ProposalState) -> ProposalState:
    return await VerifierAgent().run(state)


async def extraction_node(state: ProposalState) -> ProposalState:
    return await ExtractionAgent().run(state)


def make_agent_node(
    agent_factory: Callable[[], BaseAgent],
) -> Callable:
    """Create a LangGraph node backed by an injected agent."""

    async def node(state: ProposalState) -> ProposalState:
        return await agent_factory().run(state)

    return node
