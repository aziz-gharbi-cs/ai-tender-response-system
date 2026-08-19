from app.agents.base import BaseAgent
from app.graph.state import ProposalState


class GenerationAgent(BaseAgent):
    """
    Generates the technical proposal using the LLM and retrieved context.
    """

    def __init__(self, llm_provider, retriever):
        self.llm_provider = llm_provider
        self.retriever = retriever

    async def run(self, state: ProposalState) -> ProposalState:
        state["proposal_draft"] = state.get("proposal_draft", "")
        state["status"] = "generated"

        return state
