from app.agents.base import BaseAgent
from app.graph.state import ProposalState


class ExtractionAgent(BaseAgent):
    """
    Extracts structured requirements from tender documents.
    """

    async def run(self, state: ProposalState) -> ProposalState:
        state["requirements"] = state.get("requirements", {})
        state["status"] = "extracted"

        return state
