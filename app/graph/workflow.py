from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    extraction_node,
    generation_node,
    quality_node,
    research_node,
    verifier_node,
)
from app.graph.state import ProposalState


def build_proposal_workflow():
    """
    Build the complete tender-response LangGraph workflow.
    """

    graph = StateGraph(ProposalState)

    # Register nodes
    graph.add_node("verifier", verifier_node)
    graph.add_node("extraction", extraction_node)
    graph.add_node("research", research_node)
    graph.add_node("generation", generation_node)
    graph.add_node("quality", quality_node)

    # Define workflow
    graph.add_edge(START, "verifier")
    graph.add_edge("verifier", "extraction")
    graph.add_edge("extraction", "research")
    graph.add_edge("research", "generation")
    graph.add_edge("generation", "quality")
    graph.add_edge("quality", END)

    return graph.compile()
