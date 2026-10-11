"""
ARX INVENTOR - Persistent Memory Management
Provides SQLite-backed persistence separated strictly by workspace/user identifier.
"""

import sqlite3
import json
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from config.settings import settings
from database.schema import SCHEMA_SQL

class PersistentMemory:
    """Manages SQLite persistent research memory with strict workspace isolation."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        """Initializes tables and indices."""
        with self._get_connection() as conn:
            conn.executescript(SCHEMA_SQL)

    def get_or_create_workspace(self, workspace_id: str) -> str:
        """Ensures a workspace exists."""
        clean_id = workspace_id.strip() or "default_workspace"
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO workspaces (workspace_id) VALUES (?)",
                (clean_id,)
            )
        return clean_id

    def create_session(self, workspace_id: str, title: str, research_question: str, scope_config: Dict[str, Any]) -> str:
        """Creates a new research session record isolated to workspace."""
        self.get_or_create_workspace(workspace_id)
        session_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO research_sessions (id, workspace_id, title, research_question, status, scope_config)
                VALUES (?, ?, ?, ?, 'draft', ?)
                """,
                (session_id, workspace_id, title, research_question, json.dumps(scope_config))
            )
        return session_id

    def update_session_plan(self, session_id: str, plan: Dict[str, Any], status: str = "plan_created"):
        """Saves or updates the structured research plan."""
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE research_sessions
                SET research_plan = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (json.dumps(plan), status, session_id)
            )

    def update_session_status(self, session_id: str, status: str):
        """Updates session execution status."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE research_sessions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, session_id)
            )

    def save_sources(self, session_id: str, sources: List[Dict[str, Any]]):
        """Saves retrieved source records."""
        with self._get_connection() as conn:
            for s in sources:
                source_id = s.get("id") or str(uuid.uuid4())
                metadata = s.get("metadata", {})
                conn.execute(
                    """
                    INSERT INTO sources (id, session_id, source_id_label, source_type, title, identifier, page_or_section, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source_id,
                        session_id,
                        s.get("source_id_label", "S1"),
                        s.get("source_type", "document"),
                        s.get("title", "Untitled Source"),
                        s.get("identifier", "Unknown"),
                        str(s.get("page_or_section", "")),
                        json.dumps(metadata)
                    )
                )

    def save_evidence_items(self, session_id: str, evidence_items: List[Dict[str, Any]]):
        """Saves extracted claims and quotations."""
        with self._get_connection() as conn:
            for ev in evidence_items:
                ev_id = ev.get("id") or str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO evidence_items (id, session_id, source_id_label, passage_text, claim, page_number, confidence_score, support_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ev_id,
                        session_id,
                        ev.get("source_id_label", "S1"),
                        ev.get("passage_text", ""),
                        ev.get("claim", ""),
                        ev.get("page_number"),
                        float(ev.get("confidence_score", 1.0)),
                        ev.get("support_status", "supported")
                    )
                )

    def save_contradiction(self, session_id: str, contradiction: Dict[str, Any]):
        """Saves identified contradictory claims and reconciliation status."""
        c_id = contradiction.get("id") or str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO contradictions (id, session_id, metric_or_topic, source_a_label, claim_a, source_b_label, claim_b, reconciliation_analysis, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    c_id,
                    session_id,
                    contradiction.get("metric_or_topic", ""),
                    contradiction.get("source_a_label", "S1"),
                    contradiction.get("claim_a", ""),
                    contradiction.get("source_b_label", "S2"),
                    contradiction.get("claim_b", ""),
                    contradiction.get("reconciliation_analysis", ""),
                    contradiction.get("status", "unresolved")
                )
            )

    def save_report(self, session_id: str, report_markdown: str, report_json: Optional[Dict[str, Any]] = None, citation_score: float = 1.0) -> str:
        """Saves a research briefing report version."""
        report_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            # Determine version
            cur = conn.execute("SELECT COUNT(*) as cnt FROM reports WHERE session_id = ?", (session_id,))
            version = (cur.fetchone()["cnt"] or 0) + 1

            conn.execute(
                """
                INSERT INTO reports (id, session_id, version, report_markdown, report_json, citation_score)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    session_id,
                    version,
                    report_markdown,
                    json.dumps(report_json or {}),
                    citation_score
                )
            )
            conn.execute(
                "UPDATE research_sessions SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )
        return report_id

    def save_feedback(self, session_id: str, report_id: str, rating: int, feedback_text: str):
        """Saves user rating and evaluation feedback."""
        fb_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO report_feedback (id, session_id, report_id, rating, feedback_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (fb_id, session_id, report_id, rating, feedback_text)
            )

    def list_sessions(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Lists all research sessions for a workspace."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, workspace_id, title, research_question, status, created_at, updated_at
                FROM research_sessions
                WHERE workspace_id = ?
                ORDER BY updated_at DESC
                """,
                (workspace_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_session(self, session_id: str, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Fetches full session details isolated to workspace."""
        with self._get_connection() as conn:
            session_row = conn.execute(
                "SELECT * FROM research_sessions WHERE id = ? AND workspace_id = ?",
                (session_id, workspace_id)
            ).fetchone()
            if not session_row:
                return None
            session_data = dict(session_row)
            if session_data.get("scope_config"):
                session_data["scope_config"] = json.loads(session_data["scope_config"])
            if session_data.get("research_plan"):
                session_data["research_plan"] = json.loads(session_data["research_plan"])

            # Fetch sources
            src_rows = conn.execute(
                "SELECT * FROM sources WHERE session_id = ? ORDER BY source_id_label ASC",
                (session_id,)
            ).fetchall()
            session_data["sources"] = [dict(r) for r in src_rows]

            # Fetch evidence
            ev_rows = conn.execute(
                "SELECT * FROM evidence_items WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,)
            ).fetchall()
            session_data["evidence"] = [dict(r) for r in ev_rows]

            # Fetch contradictions
            ct_rows = conn.execute(
                "SELECT * FROM contradictions WHERE session_id = ?",
                (session_id,)
            ).fetchall()
            session_data["contradictions"] = [dict(r) for r in ct_rows]

            # Fetch reports
            rep_rows = conn.execute(
                "SELECT * FROM reports WHERE session_id = ? ORDER BY version DESC",
                (session_id,)
            ).fetchall()
            session_data["reports"] = [dict(r) for r in rep_rows]

            # Fetch feedback
            fb_rows = conn.execute(
                "SELECT * FROM report_feedback WHERE session_id = ?",
                (session_id,)
            ).fetchall()
            session_data["feedback"] = [dict(r) for r in fb_rows]

            return session_data

    def delete_session(self, session_id: str, workspace_id: str) -> bool:
        """Deletes a specific session for a given workspace."""
        with self._get_connection() as conn:
            cur = conn.execute(
                "DELETE FROM research_sessions WHERE id = ? AND workspace_id = ?",
                (session_id, workspace_id)
            )
            return cur.rowcount > 0

    def clear_workspace_memory(self, workspace_id: str) -> bool:
        """Clears all stored sessions for a given workspace."""
        with self._get_connection() as conn:
            cur = conn.execute(
                "DELETE FROM research_sessions WHERE workspace_id = ?",
                (workspace_id,)
            )
            return cur.rowcount >= 0

    def get_workspace_stats(self, workspace_id: str) -> Dict[str, int]:
        """Calculates genuine summary statistics for a workspace."""
        with self._get_connection() as conn:
            s_cnt = conn.execute(
                "SELECT COUNT(*) as cnt FROM research_sessions WHERE workspace_id = ?",
                (workspace_id,)
            ).fetchone()["cnt"] or 0

            rep_cnt = conn.execute(
                """
                SELECT COUNT(*) as cnt FROM reports
                JOIN research_sessions ON reports.session_id = research_sessions.id
                WHERE research_sessions.workspace_id = ?
                """,
                (workspace_id,)
            ).fetchone()["cnt"] or 0

            ct_cnt = conn.execute(
                """
                SELECT COUNT(*) as cnt FROM contradictions
                JOIN research_sessions ON contradictions.session_id = research_sessions.id
                WHERE research_sessions.workspace_id = ?
                """,
                (workspace_id,)
            ).fetchone()["cnt"] or 0

            ev_cnt = conn.execute(
                """
                SELECT COUNT(*) as cnt FROM evidence_items
                JOIN research_sessions ON evidence_items.session_id = research_sessions.id
                WHERE research_sessions.workspace_id = ?
                """,
                (workspace_id,)
            ).fetchone()["cnt"] or 0

            return {
                "sessions_count": s_cnt,
                "reports_count": rep_cnt,
                "contradictions_count": ct_cnt,
                "evidence_count": ev_cnt
            }

    def get_all_workspace_evidence(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Retrieves all evidence claims across sessions in a workspace."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT e.*, s.title as session_title, s.research_question
                FROM evidence_items e
                JOIN research_sessions s ON e.session_id = s.id
                WHERE s.workspace_id = ?
                ORDER BY e.created_at DESC
                """,
                (workspace_id,)
            ).fetchall()
            return [dict(r) for r in rows]

