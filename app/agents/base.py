from abc import ABC, abstractmethod

from app.graph.state import ProposalState


class BaseAgent(ABC):
    """
    Base contract for all AI agents in the tender-response workflow.
    """

    @abstractmethod
    async def run(self, state: ProposalState) -> ProposalState:
        """
        Execute the agent against the shared workflow state.
        """
        raise NotImplementedError
