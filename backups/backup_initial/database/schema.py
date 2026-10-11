"""
ARX INVENTOR - Database Schema Definitions
Provides SQL DDL for SQLite persistent research memory with strict workspace isolation.
"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_sessions (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    title TEXT NOT NULL,
    research_question TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    scope_config TEXT,
    research_plan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_workspace ON research_sessions(workspace_id);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    source_id_label TEXT NOT NULL,
    source_type TEXT NOT NULL,
    title TEXT NOT NULL,
    identifier TEXT NOT NULL,
    page_or_section TEXT,
    retrieval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT,
    FOREIGN KEY(session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sources_session ON sources(session_id);

CREATE TABLE IF NOT EXISTS evidence_items (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    source_id_label TEXT NOT NULL,
    passage_text TEXT NOT NULL,
    claim TEXT,
    page_number INTEGER,
    confidence_score REAL DEFAULT 1.0,
    support_status TEXT DEFAULT 'supported',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_evidence_session ON evidence_items(session_id);

CREATE TABLE IF NOT EXISTS contradictions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    metric_or_topic TEXT NOT NULL,
    source_a_label TEXT NOT NULL,
    claim_a TEXT NOT NULL,
    source_b_label TEXT NOT NULL,
    claim_b TEXT NOT NULL,
    reconciliation_analysis TEXT,
    status TEXT DEFAULT 'unresolved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_contradictions_session ON contradictions(session_id);

CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    report_markdown TEXT NOT NULL,
    report_json TEXT,
    citation_score REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reports_session ON reports(session_id);

CREATE TABLE IF NOT EXISTS report_feedback (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    report_id TEXT NOT NULL,
    rating INTEGER,
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES research_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_feedback_session ON report_feedback(session_id);
"""
