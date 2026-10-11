"""
ARX INVENTOR - Session Memory
Maintains live runtime state for an active research session:
current question, plan, retrieved evidence, agent timeline events, draft report, and approvals.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time

@dataclass
class TimelineEvent:
    timestamp: float = field(default_factory=time.time)
    agent_name: str = ""
    action: str = ""
    status: str = "running" # "running", "completed", "warning", "failed"
    details: str = ""
    tool_name: Optional[str] = None
    tool_result_summary: Optional[str] = None

class SessionMemory:
    """Manages active research session runtime memory."""

    def __init__(self, workspace_id: str = "default_workspace"):
        self.workspace_id = workspace_id
        self.session_id: Optional[str] = None
        self.research_question: str = ""
        self.scope_config: Dict[str, Any] = {}
        self.research_plan: Optional[Dict[str, Any]] = None
        self.plan_approved: bool = False
        
        # Working state
        self.retrieved_sources: List[Dict[str, Any]] = []
        self.retrieved_chunks: List[Dict[str, Any]] = []
        self.extracted_claims: List[Dict[str, Any]] = []
        self.contradictions: List[Dict[str, Any]] = []
        self.unanswered_subquestions: List[str] = []
        
        # Reports
        self.draft_report: Optional[str] = None
        self.final_report: Optional[str] = None
        self.citation_score: float = 0.0
        self.report_approved: bool = False
        
        # Timeline
        self.timeline: List[TimelineEvent] = []

    def reset(self, workspace_id: Optional[str] = None):
        """Clears in-memory session state."""
        if workspace_id:
            self.workspace_id = workspace_id
        self.session_id = None
        self.research_question = ""
        self.scope_config = {}
        self.research_plan = None
        self.plan_approved = False
        self.retrieved_sources.clear()
        self.retrieved_chunks.clear()
        self.extracted_claims.clear()
        self.contradictions.clear()
        self.unanswered_subquestions.clear()
        self.draft_report = None
        self.final_report = None
        self.citation_score = 0.0
        self.report_approved = False
        self.timeline.clear()

    def add_timeline_event(self, agent_name: str, action: str, status: str = "completed", details: str = "", tool_name: Optional[str] = None, tool_result_summary: Optional[str] = None):
        """Records an observable timeline step."""
        evt = TimelineEvent(
            timestamp=time.time(),
            agent_name=agent_name,
            action=action,
            status=status,
            details=details,
            tool_name=tool_name,
            tool_result_summary=tool_result_summary
        )
        self.timeline.append(evt)
        return evt

    def add_source(self, source: Dict[str, Any]):
        """Adds a source if not already present."""
        existing = [s["identifier"] for s in self.retrieved_sources]
        if source.get("identifier") not in existing:
            self.retrieved_sources.append(source)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Adds retrieved RAG chunks."""
        self.retrieved_chunks.extend(chunks)

    def add_claims(self, claims: List[Dict[str, Any]]):
        """Adds extracted factual claims."""
        self.extracted_claims.extend(claims)

    def add_contradiction(self, contradiction: Dict[str, Any]):
        """Records a detected contradiction."""
        self.contradictions.append(contradiction)
