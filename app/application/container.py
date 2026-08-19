from dataclasses import dataclass

from app.agents.generation import GenerationAgent
from app.agents.quality import QualityAgent
from app.agents.research import ResearchAgent


@dataclass
class ApplicationContainer:
    """
    Central composition root for application dependencies.

    Concrete infrastructure implementations will be injected here.
    """

    research_provider: object
    llm_provider: object
    retriever: object
    security_scanner: object

    def create_research_agent(self) -> ResearchAgent:
        return ResearchAgent(
            research_provider=self.research_provider,
        )

    def create_generation_agent(self) -> GenerationAgent:
        return GenerationAgent(
            llm_provider=self.llm_provider,
            retriever=self.retriever,
        )

    def create_quality_agent(self) -> QualityAgent:
        return QualityAgent(
            security_scanner=self.security_scanner,
        )
