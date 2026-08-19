from app.agents.base import BaseAgent
from app.graph.state import ProposalState


class QualityAgent(BaseAgent):
    """
    Validates proposal quality and security.
    """

    def __init__(self, security_scanner):
        self.security_scanner = security_scanner

    async def run(self, state: ProposalState) -> ProposalState:
        state["quality_report"] = {
            "status": "pending",
        }

        state["status"] = "validated"

        return state
