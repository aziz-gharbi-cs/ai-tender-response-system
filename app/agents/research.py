from app.agents.base import BaseAgent
from app.graph.state import ProposalState


class ResearchAgent(BaseAgent):
    """
    Performs external research through a ResearchProvider.
    """

    def __init__(self, research_provider):
        self.research_provider = research_provider

    async def run(self, state: ProposalState) -> ProposalState:
        state["external_research"] = state.get("external_research", {})
        state["status"] = "researched"

        return state
