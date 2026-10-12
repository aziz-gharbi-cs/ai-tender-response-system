from langgraph.graph import END, START, StateGraph

from app.application.container import ApplicationContainer
from app.graph.nodes import extraction_node, make_agent_node, verifier_node
from app.graph.state import ProposalState


async def ingest_tender_node(
    state: ProposalState,
    container: ApplicationContainer,
) -> ProposalState:
    """Ingest the first tender file if extracted text was not provided."""
    if state.get("extracted_text"):
        return state

    documents = state.get("input_documents", [])
    if not documents or container.ingestion_service is None:
        return state

    try:
        document = await container.ingestion_service.ingest_document(
            documents[0]
        )
        state["document_id"] = document.document_id
        state["extracted_text"] = {
            document.filename: document.full_text
        }
    except Exception as exc:
        errors = list(state.get("errors", []))
        errors.append(f"Tender ingestion failed: {exc}")
        state["errors"] = errors
        state["status"] = "ingestion_failed"

    return state


def route_after_verifier(state: ProposalState) -> str:
    return (
        "end"
        if state.get("status") == "verification_failed"
        else "continue"
    )


def route_after_ingestion(state: ProposalState) -> str:
    return (
        "end"
        if state.get("status") == "ingestion_failed"
        else "continue"
    )


def build_proposal_workflow(container: ApplicationContainer):
    """Build the proposal workflow using configured dependencies."""
    graph = StateGraph(ProposalState)

    graph.add_node("verifier", verifier_node)
    async def ingestion_node(state: ProposalState) -> ProposalState:
        return await ingest_tender_node(state, container)

    graph.add_node("ingestion", ingestion_node)
    graph.add_node("extraction", extraction_node)
    graph.add_node("research", make_agent_node(container.create_research_agent))
    graph.add_node("generation", make_agent_node(container.create_generation_agent))
    graph.add_node("quality", make_agent_node(container.create_quality_agent))

    graph.add_edge(START, "verifier")
    graph.add_conditional_edges(
        "verifier",
        route_after_verifier,
        {"end": END, "continue": "ingestion"},
    )
    graph.add_conditional_edges(
        "ingestion",
        route_after_ingestion,
        {"end": END, "continue": "extraction"},
    )
    graph.add_edge("extraction", "research")
    graph.add_edge("research", "generation")
    graph.add_edge("generation", "quality")
    graph.add_edge("quality", END)

    return graph.compile()
