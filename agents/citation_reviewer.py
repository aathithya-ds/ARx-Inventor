"""
ARX INVENTOR - Agent 6: Citation Quality Reviewer
Role: Senior Citation Quality Auditor
Powered by: Anthropic Claude
Objective: Rigorously verifies that all report citations [S1], [S2] resolve to genuine sources,
checks that quotes match retrieved passage text, detects hallucinations, and calculates verification scores.
"""

from typing import List, Dict, Any
from tools.citation_validator import CitationValidatorTool
from services.provider_service import ProviderService

class CitationReviewerAgent:
    """Agent 6: Quality audit agent ensuring grounded citations and quotes."""

    def __init__(self, provider_service: ProviderService, validator_tool: CitationValidatorTool):
        self.provider_service = provider_service
        self.validator_tool = validator_tool
        self.role = "Lead Citation Quality Reviewer & Epistemic Auditor"
        self.goal = "Validate all in-text citations, confirm quotation authenticity against source passages, and prevent hallucinated citations."
        self.backstory = (
            "You are a strict academic editor and evidentiary auditor powered by Anthropic Claude. "
            "You verify every citation tag against indexed sources. If any claim lacks an authentic reference "
            "or quotes a passage that does not exist in the source texts, you flag the violation immediately."
        )

    def review_report_citations(
        self,
        report_markdown: str,
        retrieved_sources: List[Dict[str, Any]],
        retrieved_passages: List[Dict[str, Any]],
        demo_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Executes formal citation validation.
        Returns:
        {
            "approved": bool,
            "citation_score": float, # 0.0 to 1.0
            "validation_details": dict,
            "audit_summary": str,
            "recommended_actions": list[str]
        }
        """
        # Run programmatic tool validation
        tool_results = self.validator_tool.validate_report(
            report_markdown=report_markdown,
            retrieved_sources=retrieved_sources,
            retrieved_passages=retrieved_passages
        )

        citation_score = tool_results.get("citation_score", 0.0)
        is_valid = tool_results.get("valid", False)
        flagged = tool_results.get("flagged_issues", [])

        actions = []
        if not is_valid:
            if tool_results.get("missing_source_ids"):
                actions.append(f"Remove or rectify phantom citations: {tool_results['missing_source_ids']}")
            if any("Quoted passage not found" in f for f in flagged):
                actions.append("Re-align unverified quotes with literal source chunk text.")
            audit_summary = f"Audit flagged {len(flagged)} evidentiary compliance issue(s). Citation Score: {citation_score*100:.1f}%."
        else:
            audit_summary = f"All {tool_results.get('total_citations_found', 0)} citations successfully map to verified sources. Citation Score: {citation_score*100:.1f}%."
            actions.append("Report meets evidentiary standards. Certified for dissemination.")

        return {
            "approved": is_valid,
            "citation_score": citation_score,
            "validation_details": tool_results,
            "audit_summary": audit_summary,
            "recommended_actions": actions
        }
