from app.agents.base import BaseAgent
from app.graph.state import ProposalState


class VerifierAgent(BaseAgent):
    """
    Validates the input tender package.
    """

    async def run(self, state: ProposalState) -> ProposalState:
        documents = state.get("input_documents", [])

        if not documents:
            state["errors"] = state.get("errors", [])
            state["errors"].append("No input documents were provided.")
            state["status"] = "verification_failed"
            return state

        state["status"] = "verified"
        return state
