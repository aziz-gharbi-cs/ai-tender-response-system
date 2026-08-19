from app.graph.state import ProposalState


async def verifier_node(state: ProposalState) -> ProposalState:
    """
    Validate the tender package before processing.
    """
    state["status"] = "verified"
    return state


async def extraction_node(state: ProposalState) -> ProposalState:
    """
    Extract structured requirements from the tender documents.
    """
    state["status"] = "extracted"
    return state


async def research_node(state: ProposalState) -> ProposalState:
    """
    Perform external market and competitor research.
    """
    state["status"] = "researched"
    return state


async def generation_node(state: ProposalState) -> ProposalState:
    """
    Generate the technical proposal using internal and external context.
    """
    state["status"] = "generated"
    return state


async def quality_node(state: ProposalState) -> ProposalState:
    """
    Validate quality, consistency, security, and compliance.
    """
    state["status"] = "validated"
    return state
