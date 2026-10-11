from langgraph.graph import END, START, StateGraph

from app.application.container import ApplicationContainer
from app.graph.nodes import (
    extraction_node,
    make_agent_node,
    verifier_node,
)
from app.graph.state import ProposalState


def route_after_verifier(state: ProposalState) -> str:
    """Stop the workflow when input verification fails."""
    if state.get("status") == "verification_failed":
        return "end"
    return "continue"


def build_proposal_workflow(container: ApplicationContainer):
    """Build the proposal workflow using configured application dependencies."""

    graph = StateGraph(ProposalState)

    graph.add_node("verifier", verifier_node)
    graph.add_node("extraction", extraction_node)
    graph.add_node("research", make_agent_node(container.create_research_agent))
    graph.add_node("generation", make_agent_node(container.create_generation_agent))
    graph.add_node("quality", make_agent_node(container.create_quality_agent))

    graph.add_edge(START, "verifier")

    graph.add_conditional_edges(
        "verifier",
        route_after_verifier,
        {
            "end": END,
            "continue": "extraction",
        },
    )

    graph.add_edge("extraction", "research")
    graph.add_edge("research", "generation")
    graph.add_edge("generation", "quality")
    graph.add_edge("quality", END)

    return graph.compile()
