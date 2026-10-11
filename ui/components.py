"""
ARX INVENTOR - Reusable UI Components
Provides styled components for metrics, navigation, agent workflow status,
evidence classification cards, contradiction diffs, and document explorer.
All components are formatted without indented newlines to guarantee CommonMark
never interprets HTML tags as indented code blocks.
"""

from typing import List, Dict, Any, Optional
import html
import streamlit as st

def to_clean_html(content: str) -> str:
    """Strips line indentation and collapses newlines so CommonMark never treats HTML as code blocks."""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    return "".join(lines)

def st_html(content: str):
    """Safely renders HTML in Streamlit without CommonMark code block conversion."""
    st.markdown(to_clean_html(content), unsafe_allow_html=True)

def render_top_navbar(current_page: str, workspace_id: str, demo_mode: bool, providers_info: Dict[str, Any]) -> str:
    """Renders the sleek top navigation bar with breadcrumb and status indicators."""
    clean_page = html.escape(current_page)
    clean_ws = html.escape(workspace_id)
    
    connected_count = sum(1 for p in providers_info.values() if p.get("status") == "connected")
    total_providers = len(providers_info)
    
    if demo_mode:
        mode_pill = (
            '<div class="nav-status-pill pill-demo">'
            '<span class="nav-pulse-dot"></span>'
            '<span>Demo Simulation Mode</span>'
            '</div>'
        )
    else:
        mode_pill = (
            f'<div class="nav-status-pill pill-live">'
            f'<span class="nav-pulse-dot"></span>'
            f'<span>Live Providers ({connected_count}/{total_providers})</span>'
            f'</div>'
        )

    res = (
        f'<div class="top-nav-bar">'
        f'<div class="breadcrumbs">'
        f'<span class="breadcrumb-root">ARX INVENTOR</span>'
        f'<span class="breadcrumb-sep">/</span>'
        f'<span class="breadcrumb-root">{clean_ws}</span>'
        f'<span class="breadcrumb-sep">/</span>'
        f'<span class="breadcrumb-current"><span>{clean_page}</span></span>'
        f'</div>'
        f'<div class="nav-badges-group">'
        f'{mode_pill}'
        f'<div class="nav-status-pill"><span>Workspace: <b>{clean_ws}</b></span></div>'
        f'</div>'
        f'</div>'
    )
    return to_clean_html(res)

def render_hero_banner() -> str:
    """Renders the high-impact research workspace hero section."""
    res = (
        '<div class="arx-hero">'
        '<div class="hero-pill"><span>●</span> AI-POWERED RESEARCH WORKSPACE</div>'
        '<h1 class="hero-title">Research with evidence. <span class="gradient-text">Report with confidence.</span></h1>'
        '<p class="hero-description">'
        'Source-grounded autonomous research platform orchestrated by 6 specialized ReAct agents. '
        'Extract verbatim citations, detect cross-document contradictions, and generate verifiably backed executive briefings.'
        '</p>'
        '</div>'
    )
    return to_clean_html(res)

def render_stats_overview(sessions_count: int, docs_count: int, reports_count: int, contradictions_count: int) -> str:
    """Renders summary cards with genuine metrics from persistent storage."""
    res = (
        '<div class="stats-grid">'
        '<div class="stat-card">'
        '<div class="stat-card-header">'
        '<span class="stat-card-label">Research Sessions</span>'
        '<span class="stat-card-icon">🔬</span>'
        '</div>'
        f'<div class="stat-card-value">{sessions_count}</div>'
        '<span class="stat-card-subtext">Isolated in workspace</span>'
        '</div>'
        '<div class="stat-card">'
        '<div class="stat-card-header">'
        '<span class="stat-card-label">Documents Indexed</span>'
        '<span class="stat-card-icon">📚</span>'
        '</div>'
        f'<div class="stat-card-value">{docs_count}</div>'
        '<span class="stat-card-subtext">ChromaDB vector store</span>'
        '</div>'
        '<div class="stat-card">'
        '<div class="stat-card-header">'
        '<span class="stat-card-label">Reports Generated</span>'
        '<span class="stat-card-icon">📑</span>'
        '</div>'
        f'<div class="stat-card-value">{reports_count}</div>'
        '<span class="stat-card-subtext">Executive briefings</span>'
        '</div>'
        '<div class="stat-card">'
        '<div class="stat-card-header">'
        '<span class="stat-card-label">Contradictions Flagged</span>'
        '<span class="stat-card-icon">⚖️</span>'
        '</div>'
        f'<div class="stat-card-value">{contradictions_count}</div>'
        '<span class="stat-card-subtext">Discrepancy analyses</span>'
        '</div>'
        '</div>'
    )
    return to_clean_html(res)

def render_agent_workflow_grid(active_agent_name: Optional[str] = None, completed_agents: Optional[List[str]] = None) -> str:
    """
    Renders the 6 specialized agent roles with visual UI cards and status badges.
    """
    completed_set = set(completed_agents or [])
    
    agents = [
        {
            "id": "planner",
            "name": "1. Research Planner",
            "provider": "Google Gemini",
            "icon": "🧭",
            "desc": "Deconstructs inquiry into structured subquestions & empirical methodology.",
            "match_keys": ["Research Planner", "Planner", "Document Ingestion"]
        },
        {
            "id": "retriever",
            "name": "2. Source Retriever",
            "provider": "RAG & Approved Web",
            "icon": "🔍",
            "desc": "Cosine similarity retrieval on ChromaDB with domain guardrails.",
            "match_keys": ["Source Retriever", "Document Reader", "RAG Retriever"]
        },
        {
            "id": "extractor",
            "name": "3. Evidence Extractor",
            "provider": "OpenAI GPT-4o-mini",
            "icon": "⚡",
            "desc": "Extracts verifiable claims with verbatim quotes & page references.",
            "match_keys": ["Evidence Extractor", "Extractor"]
        },
        {
            "id": "analyst",
            "name": "4. Research Analyst",
            "provider": "Multi-Source Reasoning",
            "icon": "⚖️",
            "desc": "Identifies numerical discrepancies and reconciles conflicting data.",
            "match_keys": ["Research Analyst", "Analyst"]
        },
        {
            "id": "writer",
            "name": "5. Synthesis Writer",
            "provider": "OpenAI GPT-4o-mini",
            "icon": "📝",
            "desc": "Synthesizes 14-section structured briefing with strict epistemic standards.",
            "match_keys": ["Synthesis Writer", "Writer"]
        },
        {
            "id": "reviewer",
            "name": "6. Citation Quality Reviewer",
            "provider": "Anthropic Claude",
            "icon": "🛡️",
            "desc": "Audits citation validity, verifies quote accuracy & computes trust score.",
            "match_keys": ["Citation Reviewer", "Reviewer", "Citation Quality Reviewer", "Complete"]
        }
    ]

    cards_html = []
    for ag in agents:
        is_active = False
        is_completed = False
        
        if active_agent_name:
            for k in ag["match_keys"]:
                if k.lower() in active_agent_name.lower():
                    is_active = True
                    break
        
        for k in ag["match_keys"]:
            if k in completed_set:
                is_completed = True
                break

        if is_active:
            state_class = "status-active"
            badge = '<span class="agent-state-badge agent-state-running">● RUNNING</span>'
        elif is_completed:
            state_class = "status-completed"
            badge = '<span class="agent-state-badge agent-state-completed">✓ VERIFIED</span>'
        else:
            state_class = ""
            badge = '<span class="agent-state-badge agent-state-idle">○ IDLE</span>'

        card = (
            f'<div class="agent-node {state_class}">'
            f'<div class="agent-node-header">'
            f'<div class="agent-role-pill">'
            f'<div class="agent-icon-box">{ag["icon"]}</div>'
            f'<div>'
            f'<div class="agent-name">{ag["name"]}</div>'
            f'<div class="agent-model-tag">{ag["provider"]}</div>'
            f'</div>'
            f'</div>'
            f'{badge}'
            f'</div>'
            f'<div class="agent-desc">{ag["desc"]}</div>'
            f'</div>'
        )
        cards_html.append(card)

    res = f'<div class="agent-grid">{"".join(cards_html)}</div>'
    return to_clean_html(res)

def render_evidence_card(
    claim: str,
    support_status: str,
    passage_text: str,
    source_label: str,
    doc_name: str,
    page_num: int = 1,
    confidence: float = 1.0
) -> str:
    """Renders a single verified evidence card with epistemic pill badges."""
    clean_claim = html.escape(claim)
    clean_passage = html.escape(passage_text)
    clean_src = html.escape(source_label or "S1")
    clean_doc = html.escape(doc_name or "Document")
    
    status_lower = (support_status or "supported").lower()
    badge_type = "badge-supported"
    label_text = "SUPPORTED"
    
    if "partial" in status_lower:
        badge_type = "badge-partial"
        label_text = "PARTIAL EVIDENCE"
    elif "conflict" in status_lower:
        badge_type = "badge-conflicting"
        label_text = "CONFLICTING"
    elif "infer" in status_lower:
        badge_type = "badge-inference"
        label_text = "INFERENCE"
    elif "insuffic" in status_lower:
        badge_type = "badge-insufficient"
        label_text = "INSUFFICIENT"

    confidence_pill = f"<span>Confidence: {int(confidence * 100)}%</span>" if confidence is not None else ""

    res = (
        f'<div class="evidence-card">'
        f'<div class="evidence-header">'
        f'<span class="badge-epistemic {badge_type}">{label_text}</span>'
        f'<div class="evidence-meta">'
        f'<span class="evidence-source-tag">[{clean_src}]</span>'
        f'<span>{clean_doc} (Page {page_num})</span>'
        f'{confidence_pill}'
        f'</div>'
        f'</div>'
        f'<div class="evidence-claim">{clean_claim}</div>'
        f'<div class="evidence-quote">"{clean_passage}"</div>'
        f'</div>'
    )
    return to_clean_html(res)

def render_contradiction_card(
    index: int,
    topic: str,
    claim_a: str,
    src_a: str,
    claim_b: str,
    src_b: str,
    reconciliation: str,
    status: str = "unresolved"
) -> str:
    """Renders side-by-side contradiction case with reconciliation analysis."""
    clean_topic = html.escape(topic or "Discrepancy Analysis")
    clean_ca = html.escape(claim_a or "")
    clean_sa = html.escape(src_a or "S1")
    clean_cb = html.escape(claim_b or "")
    clean_sb = html.escape(src_b or "S2")
    clean_rec = html.escape(reconciliation or "Ongoing verification required.")
    clean_stat = html.escape(status or "unresolved").upper()

    res = (
        f'<div class="contradiction-card">'
        f'<div class="contradiction-header">'
        f'<div class="contradiction-title"><span>⚠️ Case #{index}:</span> {clean_topic}</div>'
        f'<span class="badge-epistemic badge-conflicting">STATUS: {clean_stat}</span>'
        f'</div>'
        f'<div class="contradiction-split">'
        f'<div class="contradiction-side">'
        f'<div class="side-label">Source [{clean_sa}] Claim:</div>'
        f'<div style="font-size: 0.88rem; color: #F1F5F9; font-weight: 500;">{clean_ca}</div>'
        f'</div>'
        f'<div class="contradiction-side">'
        f'<div class="side-label">Source [{clean_sb}] Claim:</div>'
        f'<div style="font-size: 0.88rem; color: #F1F5F9; font-weight: 500;">{clean_cb}</div>'
        f'</div>'
        f'</div>'
        f'<div>'
        f'<div class="side-label" style="color: var(--accent-violet);">Analyst Reconciliation:</div>'
        f'<div class="reconciliation-box">{clean_rec}</div>'
        f'</div>'
        f'</div>'
    )
    return to_clean_html(res)

def render_empty_state(icon: str, title: str, description: str) -> str:
    """Renders a refined empty state."""
    res = (
        f'<div class="empty-state">'
        f'<div class="empty-state-icon">{icon}</div>'
        f'<div class="empty-state-title">{html.escape(title)}</div>'
        f'<div class="empty-state-desc">{html.escape(description)}</div>'
        f'</div>'
    )
    return to_clean_html(res)
