from typing import Any

from app.agents.base import BaseAgent
from app.graph.state import ProposalState


class QualityAgent(BaseAgent):
    """Review proposal completeness and run security scans."""

    def __init__(self, security_scanner: Any) -> None:
        self.security_scanner = security_scanner

    async def run(self, state: ProposalState) -> ProposalState:
        extracted_text = state.get("extracted_text", {})
        proposal_draft = state.get("proposal_draft", "")
        requirements = state.get("requirements", {})

        source_text = "\n\n".join(
            text for text in extracted_text.values()
            if isinstance(text, str) and text.strip()
        )

        findings: list[str] = []

        if not source_text:
            findings.append("No extracted tender text is available for review.")

        if not requirements:
            findings.append("No structured tender requirements are available.")

        if not proposal_draft.strip():
            findings.append("The proposal draft is empty.")

        input_scan: dict[str, Any] | None = None
        output_scan: dict[str, Any] | None = None
        scan_errors: list[str] = []

        try:
            if source_text:
                input_scan = await self.security_scanner.scan_input(source_text)
        except Exception as exc:
            scan_errors.append(f"Input security scan failed: {exc}")

        try:
            if proposal_draft.strip():
                output_scan = await self.security_scanner.scan_output(
                    proposal_draft
                )
        except Exception as exc:
            scan_errors.append(f"Output security scan failed: {exc}")

        if scan_errors:
            findings.extend(scan_errors)

        report = {
            "status": "reviewed",
            "security_scans": {
                "input": input_scan,
                "output": output_scan,
            },
            "findings": findings,
            "scan_errors": scan_errors,
            "proposal_present": bool(proposal_draft.strip()),
            "requirements_present": bool(requirements),
        }

        state["quality_report"] = report
        state["status"] = (
            "quality_reviewed" if not scan_errors else "quality_review_failed"
        )

        return state
