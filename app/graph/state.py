from typing import Any, TypedDict


class ProposalState(TypedDict, total=False):
    """
    Shared state for the complete tender-response workflow.
    """

    # Workflow identification
    request_id: str
    status: str

    # Input
    input_documents: list[str]
    template_path: str | None

    # Document processing
    extracted_text: dict[str, str]

    # Tender analysis
    requirements: dict[str, Any]

    # Internal knowledge
    internal_references: list[dict[str, Any]]
    candidate_profiles: list[dict[str, Any]]

    # External research
    external_research: dict[str, Any]

    # Generated content
    proposal_draft: str

    # Quality and security
    quality_report: dict[str, Any]

    # Errors / execution metadata
    errors: list[str]
