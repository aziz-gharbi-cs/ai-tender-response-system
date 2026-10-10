from dataclasses import dataclass

from app.agents.generation import GenerationAgent
from app.agents.quality import QualityAgent
from app.agents.research import ResearchAgent
from app.core.config import settings
from app.llm.provider import OllamaLLMProvider


@dataclass
class ApplicationContainer:
    """Central composition root for application dependencies."""

    research_provider: object
    llm_provider: object
    retriever: object
    security_scanner: object

    @classmethod
    def with_rag(
        cls,
        *,
        research_provider: object,
        security_scanner: object,
        llm_provider: object | None = None,
    ) -> "ApplicationContainer":
        """Build the RAG pipeline and configure the LLM provider."""
        from app.application.rag_factory import create_retrieval_service

        if llm_provider is None:
            if settings.llm_provider.lower() != "ollama":
                raise ValueError(
                    f"Unsupported LLM provider: {settings.llm_provider!r}"
                )

            llm_provider = OllamaLLMProvider(
                model=settings.llm_model,
                base_url=settings.ollama_base_url,
            )

        return cls(
            research_provider=research_provider,
            llm_provider=llm_provider,
            retriever=create_retrieval_service(),
            security_scanner=security_scanner,
        )

    def create_research_agent(self) -> ResearchAgent:
        return ResearchAgent(research_provider=self.research_provider)

    def create_generation_agent(self) -> GenerationAgent:
        return GenerationAgent(
            llm_provider=self.llm_provider,
            retriever=self.retriever,
        )

    def create_quality_agent(self) -> QualityAgent:
        return QualityAgent(security_scanner=self.security_scanner)
