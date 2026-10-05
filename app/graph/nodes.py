from app.agents.extraction import ExtractionAgent
from app.agents.verifier import VerifierAgent
from app.graph.state import ProposalState


async def verifier_node(state: ProposalState) -> ProposalState:
    agent = VerifierAgent()
    return await agent.run(state)


async def extraction_node(state: ProposalState) -> ProposalState:
    agent = ExtractionAgent()
    return await agent.run(state)


async def research_node(state: ProposalState) -> ProposalState:
    raise NotImplementedError(
        "Research node requires a ResearchProvider dependency."
    )


async def generation_node(state: ProposalState) -> ProposalState:
    raise NotImplementedError(
        "Generation node requires LLMProvider and Retriever dependencies."
    )


async def quality_node(state: ProposalState) -> ProposalState:
    raise NotImplementedError(
        "Quality node requires a SecurityScanner dependency."
    )
