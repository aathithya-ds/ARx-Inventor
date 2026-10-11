"""
ARX INVENTOR - Agent 1: Research Planner
Role: Research Planner & Scope Strategist
Powered by: Google Gemini
Objective: Understand the research question, target audience, scope, identify key subquestions,
source constraints, and produce a structured research plan.
"""

from typing import Dict, Any, List
import json
import re
from services.provider_service import ProviderService

class ResearchPlannerAgent:
    """Agent 1: Formulates structured research plan, subquestions, and strategy."""

    def __init__(self, provider_service: ProviderService):
        self.provider_service = provider_service
        self.role = "Senior Research Planning Specialist"
        self.goal = "Analyze the research question, establish rigorous investigation subquestions, identify information boundaries, and structure the search plan."
        self.backstory = (
            "You are a master research planner. You excel at deconstructing complex questions "
            "into verifiable sub-inquiries, recognizing evidentiary requirements, and identifying "
            "what information is missing before retrieval begins."
        )

    def plan_research(
        self,
        research_question: str,
        target_audience: str = "analyst",
        research_depth: str = "standard",
        report_length: str = "medium",
        source_priority: str = "documents_first",
        available_documents: List[str] = None,
        web_search_enabled: bool = True,
        additional_instructions: str = "",
        demo_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Produces a structured research plan.
        Returns:
        {
            "title": str,
            "target_audience": str,
            "scope_summary": str,
            "subquestions": list[str],
            "retrieval_strategy": str,
            "missing_info_checklist": list[str],
            "source_restrictions": dict
        }
        """
        available_docs_str = ", ".join(available_documents or []) or "No uploaded documents initially provided"

        system_prompt = (
            f"You are the {self.role}. {self.backstory}\n"
            "Produce a structured JSON plan with keys: 'title', 'scope_summary', 'subquestions', "
            "'retrieval_strategy', 'missing_info_checklist'.\n"
            "Format the output strictly as valid JSON without markdown wrapping if possible."
        )

        user_prompt = f"""
Research Question: {research_question}
Target Audience: {target_audience}
Research Depth: {research_depth}
Report Length: {report_length}
Source Priority: {source_priority}
Available Documents: {available_docs_str}
Web Search Allowed: {web_search_enabled}
Additional Instructions: {additional_instructions or 'None'}

Deconstruct this inquiry into 3 to 5 critical, verifiable subquestions.
Identify what specific data, benchmarks, or definitions must be retrieved.
Respond ONLY with a valid JSON object matching this schema:
{{
  "title": "A precise research title",
  "scope_summary": "Summary of research scope and boundaries",
  "subquestions": ["Subquestion 1", "Subquestion 2", "Subquestion 3"],
  "retrieval_strategy": "Description of retrieval strategy prioritizing documents then web sources",
  "missing_info_checklist": ["Item 1 needed to verify", "Item 2 needed to verify"]
}}
"""

        if demo_mode:
            # Deterministic high-quality plan
            return self._build_deterministic_plan(
                research_question, target_audience, research_depth, available_documents, web_search_enabled
            )

        resp = self.provider_service.generate_completion(
            provider="gemini",
            prompt=user_prompt,
            system_prompt=system_prompt,
            demo_mode=demo_mode,
            demo_task="planning"
        )

        if resp.get("simulated"):
            return self._build_deterministic_plan(
                research_question, target_audience, research_depth, available_documents, web_search_enabled,
                simulated_note=resp.get("simulated_reason")
            )

        text = resp.get("text", "")
        # Extract JSON from potential markdown codeblocks
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                parsed["source_restrictions"] = {
                    "source_priority": source_priority,
                    "web_enabled": web_search_enabled
                }
                return parsed
            except Exception:
                pass

        return self._build_deterministic_plan(
            research_question, target_audience, research_depth, available_documents, web_search_enabled
        )

    def _build_deterministic_plan(
        self,
        research_question: str,
        target_audience: str,
        research_depth: str,
        available_docs: List[str] = None,
        web_search_enabled: bool = True,
        simulated_note: str = None
    ) -> Dict[str, Any]:
        """Provides deterministic plan for demo mode or fallbacks."""
        clean_q = research_question.strip().rstrip("?")
        docs_info = f" ({len(available_docs)} uploaded files)" if available_docs else " (No files uploaded)"

        note_prefix = f"[{simulated_note}] " if simulated_note else ""

        return {
            "title": f"Investigation: {clean_q.capitalize()}",
            "target_audience": target_audience,
            "scope_summary": f"{note_prefix}Comprehensive analysis targeting '{research_question}' tailored for {target_audience} with {research_depth} depth{docs_info}.",
            "subquestions": [
                f"What core empirical data, statistics, and trends address: {clean_q}?",
                f"What definitions, methodological differences, or scope boundaries exist across sources?",
                f"Are there conflicting claims, divergent metrics, or unresolved disagreements?",
                f"What limitations and evidentiary gaps remain unanswered by current sources?"
            ],
            "retrieval_strategy": "Examine uploaded document corpus first using semantic vector similarity; cross-reference permitted web sources for validation if enabled.",
            "missing_info_checklist": [
                "Empirical baseline metrics and dates of measurement",
                "Source methodology, sample size, and jurisdictional boundaries",
                "Authoritative institutional consensus or dissenting viewpoints"
            ],
            "source_restrictions": {
                "source_priority": "documents_first",
                "web_enabled": web_search_enabled
            }
        }
