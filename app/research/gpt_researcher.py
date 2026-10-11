from typing import Any

from gpt_researcher import GPTResearcher


class GPTResearcherProvider:
    """Adapter connecting GPT Researcher to the application's provider interface."""

    async def research(self, query: str) -> dict[str, Any]:
        if not query.strip():
            raise ValueError("Research query cannot be empty.")

        researcher = GPTResearcher(
            query=query,
            report_type="research_report",
        )

        await researcher.conduct_research()
        report = await researcher.write_report()

        return {
            "query": query,
            "report": report,
            "sources": researcher.get_research_sources(),
            "source_urls": researcher.get_source_urls(),
        }
