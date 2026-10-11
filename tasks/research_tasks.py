"""
ARX INVENTOR - CrewAI Task Specifications
Defines task roles, instructions, expected outputs, and dependencies for the multi-agent workflow.
"""

from typing import Dict, Any

class ResearchTasks:
    """Provides structured task definitions for CrewAI execution."""

    @staticmethod
    def create_planning_task(agent, research_question: str, scope_config: Dict[str, Any]):
        return {
            "description": (
                f"Analyze the research question '{research_question}' for the target audience "
                f"'{scope_config.get('target_audience', 'analyst')}'. Formulate 3-5 investigative subquestions, "
                f"define information boundaries, and establish search parameters prioritizing uploaded documents."
            ),
            "expected_output": "A structured JSON plan with title, scope_summary, subquestions, and retrieval_strategy.",
            "agent": agent
        }

    @staticmethod
    def create_retrieval_task(agent, subquestions: list, enable_web: bool):
        return {
            "description": (
                f"Execute semantic vector search and permitted web queries for the subquestions: {subquestions}. "
                f"Enforce domain allowlists. Register all sources with unique IDs [S1], [S2], titles, and page numbers."
            ),
            "expected_output": "A list of retrieved evidence passages with document metadata and registered sources.",
            "agent": agent
        }

    @staticmethod
    def create_extraction_task(agent, passages: list):
        return {
            "description": (
                f"Inspect the retrieved passages. Extract verifiable claims with exact verbatim excerpts, "
                f"source labels, page numbers, and epistemic confidence ratings."
            ),
            "expected_output": "A structured list of verified claims and verbatim passages.",
            "agent": agent
        }

    @staticmethod
    def create_analysis_task(agent, claims: list):
        return {
            "description": (
                f"Compare the extracted claims across different sources. Detect multi-source agreements, "
                f"contradictory statistics or percentages (e.g. 35% vs 48%), and evidentiary blind spots."
            ),
            "expected_output": "A comparative analysis report detailing agreements, contradictions, and data gaps.",
            "agent": agent
        }

    @staticmethod
    def create_synthesis_task(agent, report_length: str):
        return {
            "description": (
                f"Draft an authoritative, objective 14-section research briefing of length '{report_length}'. "
                f"Tie every factual claim to its [S#] citation and page number. Explicitly present contradictory metrics."
            ),
            "expected_output": "A complete 14-section markdown research report with inline citations.",
            "agent": agent
        }

    @staticmethod
    def create_citation_review_task(agent):
        return {
            "description": (
                "Audit the briefing report against indexed sources. Ensure all citations map to real sources, "
                "verify that quoted strings exist in retrieved passages, and calculate compliance score."
            ),
            "expected_output": "A citation audit certifying compliance or recommending exact corrections.",
            "agent": agent
        }
