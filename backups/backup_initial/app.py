"""
ARX INVENTOR — Research Assistant with Source-Based Briefing
Premium AI Research Platform & Verifiable Multi-Agent Workspace
"""

import streamlit as st
import os
import sys
from pathlib import Path
import json
import datetime
import subprocess

# Ensure base dir in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import settings
from memory.session_memory import SessionMemory
from memory.persistent_memory import PersistentMemory
from services.provider_service import ProviderService, ProviderStatus
from services.research_service import ResearchService
from services.report_service import ReportService
from tools.document_reader import DocumentReaderTool
from tools.rag_retriever import RAGRetrieverTool
from ui.styles import get_custom_css
from ui.components import (
    render_top_navbar,
    render_hero_banner,
    render_stats_overview,
    render_agent_workflow_grid,
    render_evidence_card,
    render_contradiction_card,
    render_empty_state
)

# Streamlit Page Configuration
st.set_page_config(
    page_title="ARX INVENTOR — AI Research Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Premium Design System CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize Session State
if "workspace_id" not in st.session_state:
    st.session_state.workspace_id = settings.DEFAULT_WORKSPACE_ID
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = settings.DEMO_MODE or not bool(
        settings.GEMINI_API_KEY and settings.OPENAI_API_KEY and settings.ANTHROPIC_API_KEY
    )
if "session_mem" not in st.session_state:
    st.session_state.session_mem = SessionMemory(st.session_state.workspace_id)
if "persist_mem" not in st.session_state:
    st.session_state.persist_mem = PersistentMemory()
if "providers" not in st.session_state:
    st.session_state.providers = ProviderService()
if "report_service" not in st.session_state:
    st.session_state.report_service = ReportService()
if "research_service" not in st.session_state:
    st.session_state.research_service = ResearchService(
        session_memory=st.session_state.session_mem,
        persistent_memory=st.session_state.persist_mem,
        provider_service=st.session_state.providers
    )
if "latest_result" not in st.session_state:
    st.session_state.latest_result = None
if "active_agent" not in st.session_state:
    st.session_state.active_agent = None
if "completed_agents" not in st.session_state:
    st.session_state.completed_agents = []
if "nav_radio" not in st.session_state:
    st.session_state.nav_radio = "Dashboard"

NAV_OPTIONS = [
    "Dashboard",
    "New Research",
    "Research Results",
    "Document Library",
    "Evidence Explorer",
    "Research History",
    "Evaluation & Testing",
    "API Configuration",
    "Settings"
]

NAV_ICONS = {
    "Dashboard": "📊",
    "New Research": "🔬",
    "Research Results": "📑",
    "Document Library": "📚",
    "Evidence Explorer": "📜",
    "Research History": "🗄️",
    "Evaluation & Testing": "🧪",
    "API Configuration": "🔑",
    "Settings": "⚙️"
}

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="arx-brand">
            <div class="arx-brand-icon">🔬</div>
            <div class="arx-brand-text">
                <span class="arx-brand-title">ARX INVENTOR</span>
                <span class="arx-brand-sub">Verifiable AI Workspace</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    current_nav_index = NAV_OPTIONS.index(st.session_state.nav_radio) if st.session_state.nav_radio in NAV_OPTIONS else 0
    selected_nav = st.radio(
        "Workspace Navigation",
        options=NAV_OPTIONS,
        index=current_nav_index,
        format_func=lambda x: f"{NAV_ICONS.get(x, '•')}  {x}",
        label_visibility="collapsed"
    )
    if selected_nav != st.session_state.nav_radio:
        st.session_state.nav_radio = selected_nav
        st.rerun()

    st.markdown("<hr style='border-color: #28344C; margin: 18px 0;'>", unsafe_allow_html=True)

    # Runtime Mode
    st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#A6B2C8; text-transform:uppercase; margin-bottom:6px;'>Runtime Mode</p>", unsafe_allow_html=True)
    demo_toggle = st.toggle(
        "Demo / Simulation Mode",
        value=st.session_state.demo_mode,
        help="Simulates LLM completions with verified benchmark facts when live API keys are not supplied."
    )
    if demo_toggle != st.session_state.demo_mode:
        st.session_state.demo_mode = demo_toggle
        st.rerun()

    # Active Workspace
    st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#A6B2C8; text-transform:uppercase; margin-bottom:6px; margin-top:14px;'>Active Workspace</p>", unsafe_allow_html=True)
    ws_input = st.text_input("Workspace Identifier", value=st.session_state.workspace_id, label_visibility="collapsed")
    if ws_input != st.session_state.workspace_id:
        st.session_state.workspace_id = ws_input
        st.session_state.session_mem.reset(ws_input)
        st.rerun()

    # Provider Status Pills
    st.markdown("<hr style='border-color: #28344C; margin: 18px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#A6B2C8; text-transform:uppercase; margin-bottom:8px;'>Provider Engine Status</p>", unsafe_allow_html=True)
    p_info = st.session_state.providers.get_provider_details()
    for p_key, p_val in p_info.items():
        stat = p_val["status"]
        if st.session_state.demo_mode:
            pill_class = "badge-inference"
            label = "Simulated"
        elif stat == ProviderStatus.CONNECTED:
            pill_class = "badge-supported"
            label = "Connected"
        elif stat == ProviderStatus.CONFIGURED:
            pill_class = "badge-partial"
            label = "Configured"
        else:
            pill_class = "badge-conflicting"
            label = "No Key"

        st.markdown(
            f"""
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; font-size:0.82rem;">
                <span style="color:#CBD5E1;">{p_val['name'].split()[0]}</span>
                <span class="badge-epistemic {pill_class}">{label}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# Render Top Navigation Bar across all pages
st.markdown(
    render_top_navbar(
        current_page=st.session_state.nav_radio,
        workspace_id=st.session_state.workspace_id,
        demo_mode=st.session_state.demo_mode,
        providers_info=p_info
    ),
    unsafe_allow_html=True
)

# Helper function to gather real workspace stats
def get_live_stats():
    ws_stats = st.session_state.persist_mem.get_workspace_stats(st.session_state.workspace_id)
    # Count real documents on disk
    sample_docs = list(settings.SAMPLE_DOCS_DIR.glob("*.*"))
    upload_docs = list(settings.UPLOADS_DIR.glob("*.*"))
    total_docs = len(sample_docs) + len(upload_docs)
    return {
        "sessions": ws_stats.get("sessions_count", 0),
        "docs": total_docs,
        "reports": ws_stats.get("reports_count", 0),
        "contradictions": ws_stats.get("contradictions_count", 0)
    }

# ============================================================
# 1. DASHBOARD HOME PAGE
# ============================================================
if st.session_state.nav_radio == "Dashboard":
    st.markdown(render_hero_banner(), unsafe_allow_html=True)

    # Real Workspace Statistics
    stats = get_live_stats()
    st.markdown(
        render_stats_overview(
            sessions_count=stats["sessions"],
            docs_count=stats["docs"],
            reports_count=stats["reports"],
            contradictions_count=stats["contradictions"]
        ),
        unsafe_allow_html=True
    )

    col_quick, col_agents = st.columns([1.3, 1.0])

    with col_quick:
        st.markdown(
            """
            <div class="premium-card">
                <div class="premium-card-header">
                    <div class="card-title-group">
                        <span style="font-size:1.15rem;">⚡</span>
                        <h3 class="card-title">Quick Research Launcher</h3>
                    </div>
                    <span class="badge-epistemic badge-supported">READY</span>
                </div>
                <p style="color:#A6B2C8; font-size:0.86rem; margin-bottom:14px;">
                    Initiate an empirical investigation across indexed documents and verified sources.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        quick_query = st.text_area(
            "Investigation Inquiry",
            height=90,
            placeholder="e.g., What was the global solar photovoltaic market adoption rate and valuation in 2024?",
            label_visibility="collapsed"
        )
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("🚀 Start New Research", use_container_width=True, key="quick_start_btn"):
                if quick_query.strip():
                    st.session_state.prefill_query = quick_query
                st.session_state.nav_radio = "New Research"
                st.rerun()
        with col_btn2:
            if st.button("📚 Explore Document Library", use_container_width=True, key="quick_docs_btn"):
                st.session_state.nav_radio = "Document Library"
                st.rerun()

        # Recent Sessions Preview
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        st.markdown("### 🗄️ **Recent Research Sessions**")
        recent_sessions = st.session_state.persist_mem.list_sessions(st.session_state.workspace_id)[:3]
        if not recent_sessions:
            st.markdown(
                render_empty_state("🔬", "No Research Sessions Yet", "Launch your first research inquiry to generate an evidence-grounded briefing."),
                unsafe_allow_html=True
            )
        else:
            for s in recent_sessions:
                with st.container():
                    st.markdown(
                        f"""
                        <div class="premium-card" style="padding:14px 18px; margin-bottom:10px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div style="font-weight:600; color:#F4F7FF; font-size:0.92rem;">{s['title']}</div>
                                <span class="badge-epistemic badge-supported">{s['status'].upper()}</span>
                            </div>
                            <div style="color:#A6B2C8; font-size:0.8rem; margin-top:4px;">
                                Inquiry: {s['research_question'][:80]}... | {s['created_at']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    col_s1, col_s2 = st.columns([1, 3])
                    with col_s1:
                        if st.button("Inspect Briefing", key=f"dash_view_{s['id']}"):
                            s_detail = st.session_state.persist_mem.get_session(s["id"], st.session_state.workspace_id)
                            if s_detail and s_detail.get("reports"):
                                st.session_state.latest_result = {
                                    "session_id": s["id"],
                                    "report_markdown": s_detail["reports"][0]["report_markdown"],
                                    "citation_score": s_detail["reports"][0]["citation_score"],
                                    "sources": s_detail.get("sources", []),
                                    "passages": [],
                                    "claims": s_detail.get("evidence", []),
                                    "contradictions": s_detail.get("contradictions", []),
                                    "timeline": []
                                }
                                st.session_state.nav_radio = "Research Results"
                                st.rerun()

    with col_agents:
        st.markdown(
            """
            <div class="premium-card">
                <div class="premium-card-header">
                    <div class="card-title-group">
                        <span style="font-size:1.15rem;">🤖</span>
                        <h3 class="card-title">Multi-Agent Architecture</h3>
                    </div>
                    <span class="badge-epistemic badge-inference">6 SPECIALIZED ROLES</span>
                </div>
                <p style="color:#A6B2C8; font-size:0.84rem; line-height:1.5;">
                    ARX INVENTOR decouples autonomous inquiry into discrete epistemic stages, ensuring verifiable citations and explicit discrepancy detection.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(render_agent_workflow_grid(active_agent_name=None, completed_agents=[]), unsafe_allow_html=True)

# ============================================================
# 2. NEW RESEARCH WORKSPACE
# ============================================================
elif st.session_state.nav_radio == "New Research":
    st.markdown("## 🔬 **Research Workspace**")
    st.caption("Formulate an evidence-grounded research inquiry with verifiable multi-agent synthesis.")

    col_form, col_agents_status = st.columns([1.5, 1.1])

    with col_form:
        st.markdown("### 🎯 **Research Question & Scope**")
        default_query = st.session_state.pop("prefill_query", "")
        research_query = st.text_area(
            "Research Question",
            value=default_query,
            height=110,
            placeholder="e.g., What was the global solar photovoltaic market adoption rate and valuation in 2024?",
            help="Specify an empirical, verifiable inquiry. The system will retrieve supporting facts and cross-check contradictory claims."
        )

        st.markdown("### 📄 **Document Evidence Corpus**")
        uploaded_files = st.file_uploader(
            "Upload reference documents (PDF, TXT, Markdown)",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            help="Uploaded documents serve as primary evidence. Text is parsed with exact page numbers and indexed into ChromaDB."
        )

        use_sample_docs = st.checkbox(
            "Include Sample Contradiction Benchmark Documents (Report A: 35% vs Report B: 48%)",
            value=True,
            help="Automatically adds the two sample solar outlook reports to demonstrate multi-source contradiction detection."
        )

        st.markdown("### ⚙️ **Investigation Parameters**")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            target_audience = st.selectbox(
                "Target Audience",
                ["analyst", "researcher", "professional", "student", "executive"],
                index=0
            )
            report_length = st.selectbox(
                "Report Length",
                ["medium", "detailed", "short"],
                index=0
            )
        with col_p2:
            research_depth = st.selectbox(
                "Research Depth",
                ["standard", "comprehensive", "basic"],
                index=0
            )
            source_priority = st.selectbox(
                "Source Priority",
                ["documents_first", "web_sources_first", "balanced"],
                index=0
            )

        with st.expander("🌐 **Web Search & Domain Guardrails**", expanded=False):
            enable_web = st.checkbox("Enable Approved Web Search", value=False)
            allowed_domains_input = st.text_input(
                "Allowed Domains (comma-separated)",
                placeholder="e.g., nature.com, iea.org, reuters.com"
            )
            excluded_domains_input = st.text_input(
                "Excluded Domains (comma-separated)",
                placeholder="e.g., wikipedia.org, untrustedblog.com"
            )
            addl_instructions = st.text_area(
                "Special Research Instructions",
                placeholder="e.g., Focus specifically on OECD grid interconnection metrics."
            )

        st.markdown("<hr style='border-color: #28344C; margin: 20px 0;'>", unsafe_allow_html=True)
        start_btn = st.button("🚀 Start Evidence-Based Research", use_container_width=True)

    with col_agents_status:
        st.markdown("### 🤖 **Agent Workflow Status**")
        st.caption("Observable ReAct coordination across 6 specialized LLM and retrieval agents.")
        
        status_placeholder = st.empty()
        status_placeholder.markdown(
            render_agent_workflow_grid(
                active_agent_name=st.session_state.active_agent,
                completed_agents=st.session_state.completed_agents
            ),
            unsafe_allow_html=True
        )

        progress_placeholder = st.empty()

    if start_btn:
        is_valid, err_msg = st.session_state.research_service.validate_inputs(research_query)
        if not is_valid:
            st.error(f"❌ {err_msg}")
        else:
            file_paths = []
            if uploaded_files:
                for uf in uploaded_files:
                    save_dest = settings.UPLOADS_DIR / uf.name
                    save_dest.write_bytes(uf.getbuffer())
                    file_paths.append(save_dest)

            if use_sample_docs:
                for s_name in ["Solar_Energy_Outlook_Report_A.txt", "Solar_Energy_Outlook_Report_B.txt"]:
                    s_path = settings.SAMPLE_DOCS_DIR / s_name
                    if s_path.exists() and s_path not in file_paths:
                        file_paths.append(s_path)

            allowed_domains = [d.strip() for d in allowed_domains_input.split(",") if d.strip()]
            excluded_domains = [d.strip() for d in excluded_domains_input.split(",") if d.strip()]

            scope_config = {
                "target_audience": target_audience,
                "research_depth": research_depth,
                "report_length": report_length,
                "source_priority": source_priority,
                "enable_web_search": enable_web,
                "allowed_domains": allowed_domains,
                "excluded_domains": excluded_domains or settings.DEFAULT_EXCLUDED_DOMAINS,
                "additional_instructions": addl_instructions
            }

            p_bar = progress_placeholder.progress(0.1, text="Agent 1 (Gemini): Formulating research plan and subquestions...")
            st.session_state.completed_agents = []

            try:
                def update_progress(agent_name, message):
                    st.session_state.active_agent = agent_name
                    if agent_name not in st.session_state.completed_agents:
                        st.session_state.completed_agents.append(agent_name)
                    status_placeholder.markdown(
                        render_agent_workflow_grid(
                            active_agent_name=agent_name,
                            completed_agents=st.session_state.completed_agents
                        ),
                        unsafe_allow_html=True
                    )
                    progress_map = {
                        "Document Ingestion": 0.20,
                        "Research Planner": 0.35,
                        "Source Retriever": 0.55,
                        "Evidence Extractor": 0.70,
                        "Research Analyst": 0.85,
                        "Synthesis Writer": 0.92,
                        "Citation Reviewer": 0.98,
                        "Complete": 1.00
                    }
                    val = progress_map.get(agent_name, 0.5)
                    p_bar.progress(val, text=f"**{agent_name}**: {message}")

                result = st.session_state.research_service.execute_research_workflow(
                    research_question=research_query,
                    scope_config=scope_config,
                    uploaded_file_paths=file_paths,
                    workspace_id=st.session_state.workspace_id,
                    demo_mode=st.session_state.demo_mode,
                    on_progress=update_progress
                )
                p_bar.progress(1.0, text="✅ Research Briefing synthesized and citations verified.")
                st.session_state.active_agent = None
                st.session_state.completed_agents = [
                    "Research Planner", "Source Retriever", "Evidence Extractor",
                    "Research Analyst", "Synthesis Writer", "Citation Reviewer"
                ]
                status_placeholder.markdown(
                    render_agent_workflow_grid(
                        active_agent_name=None,
                        completed_agents=st.session_state.completed_agents
                    ),
                    unsafe_allow_html=True
                )
                st.session_state.latest_result = result
                st.success("🎉 Research briefing successfully produced! Navigating to Results view...")
                st.session_state.nav_radio = "Research Results"
                st.rerun()
            except Exception as e:
                st.error(f"❌ Execution encountered an error: {str(e)}")

# ============================================================
# 3. RESEARCH RESULTS PAGE
# ============================================================
elif st.session_state.nav_radio == "Research Results":
    if not st.session_state.latest_result:
        st.markdown(
            render_empty_state(
                icon="📑",
                title="No Active Research Results",
                description="Launch a new inquiry in the Research Workspace or load a prior session from Research History."
            ),
            unsafe_allow_html=True
        )
        col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
        with col_c2:
            if st.button("🚀 Start New Research Now", use_container_width=True):
                st.session_state.nav_radio = "New Research"
                st.rerun()
    else:
        res = st.session_state.latest_result

        # Briefing Header Banner
        st.markdown(
            f"""
            <div class="premium-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div class="hero-pill">EVIDENTIARY RESEARCH BRIEFING</div>
                        <h2 style="margin:4px 0 8px 0; color:#F4F7FF;">{res.get('title', 'Empirical Investigation Report')}</h2>
                        <p style="color:#A6B2C8; font-size:0.88rem; margin:0;">
                            Session ID: <code>{res.get('session_id', 'N/A')[:8]}</code> | Workspace: <code>{st.session_state.workspace_id}</code>
                        </p>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <span class="badge-epistemic badge-supported">AUDITED BY CLAUDE</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Summary Metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Citation Score", f"{res['citation_score']*100:.1f}%", help="Percentage of in-text citations mapping to verified source passages")
        with col_m2:
            st.metric("Sources Indexed", len(res.get("sources", [])))
        with col_m3:
            st.metric("Evidence Passages", len(res.get("passages", [])))
        with col_m4:
            st.metric("Contradictions Flagged", len(res.get("contradictions", [])))

        # Results Tabs
        tab_report, tab_findings, tab_evidence, tab_compare, tab_sources, tab_timeline, tab_export = st.tabs([
            "📑 Full Briefing",
            "🔍 Key Findings",
            "📜 Evidence & Citations",
            "⚖️ Source Comparison & Contradictions",
            "📚 Source Registry",
            "⏱️ Activity Timeline",
            "💾 Export Briefing"
        ])

        with tab_report:
            st.markdown(
                """
                <div class="premium-card">
                """,
                unsafe_allow_html=True
            )
            st.markdown(res.get("report_markdown", "*No briefing content available.*"))
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_findings:
            st.markdown("### **Verified Empirical Claims**")
            st.caption("Discrete claims extracted by Agent 3 (OpenAI) with source page attribution.")
            claims = res.get("claims", [])
            if not claims:
                st.info("No claims recorded for this briefing.")
            else:
                for idx, c in enumerate(claims):
                    st.markdown(
                        render_evidence_card(
                            claim=c.get("claim", ""),
                            support_status=c.get("support_status", "supported"),
                            passage_text=c.get("passage_text", ""),
                            source_label=c.get("source_id_label", "S1"),
                            doc_name=c.get("document_name", "Document"),
                            page_num=c.get("page_number", 1),
                            confidence=c.get("confidence_score", 1.0)
                        ),
                        unsafe_allow_html=True
                    )

        with tab_evidence:
            st.markdown("### **Interactive Citation Inspector**")
            st.caption("Select a citation reference label [S1], [S2] to inspect its document origin, page number, and verbatim passage.")
            source_labels = [s.get("source_id_label", "S1") for s in res.get("sources", [])]
            if source_labels:
                selected_label = st.selectbox("Inspect Citation ID:", source_labels, index=0)
                insp_data = st.session_state.report_service.inspect_citation(
                    selected_label,
                    res.get("sources", []),
                    res.get("passages", [])
                )
                if insp_data.get("source"):
                    src = insp_data["source"]
                    st.markdown(
                        f"""
                        <div class="premium-card">
                            <h4 style="margin:0 0 6px 0; color:#5B8CFF;">Source [{selected_label}]: {src.get('identifier')}</h4>
                            <p style="color:#A6B2C8; font-size:0.85rem; margin:0;">
                                Type: <code>{src.get('source_type')}</code> | Coverage: <i>{src.get('page_or_section')}</i>
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.markdown("#### **Retrieved Evidence Chunks:**")
                    passages_found = insp_data.get("passages", [])
                    if not passages_found:
                        st.info("No passage excerpts cached for this citation.")
                    else:
                        for p in passages_found:
                            st.info(f"📄 **Page {p.get('page_number', 1)}** (Similarity: {p.get('score', 1.0)})\n\n> \"{p.get('text')}\"")
            else:
                st.info("No sources registered for this session.")

        with tab_compare:
            st.markdown("### **Comparative Analysis & Disagreements**")
            st.caption("Multi-source divergence analysis performed by Agent 4 (Research Analyst).")
            contradictions = res.get("contradictions", [])
            if contradictions:
                st.warning(f"⚠️ **{len(contradictions)} Contradictory Metric(s) Identified Across Sources:**")
                for idx, c in enumerate(contradictions):
                    st.markdown(
                        render_contradiction_card(
                            index=idx+1,
                            topic=c.get("metric_or_topic", "Numerical Discrepancy"),
                            claim_a=c.get("claim_a", ""),
                            src_a=c.get("source_a_label", "S1"),
                            claim_b=c.get("claim_b", ""),
                            src_b=c.get("source_b_label", "S2"),
                            reconciliation=c.get("reconciliation_analysis", ""),
                            status=c.get("status", "unresolved")
                        ),
                        unsafe_allow_html=True
                    )
            else:
                st.success("✅ **Consensus Verified:** No numerical or directional contradictions detected across retrieved evidence.")

        with tab_sources:
            st.markdown("### **Registered Sources**")
            for s in res.get("sources", []):
                st.markdown(
                    f"""
                    <div class="premium-card" style="padding:12px 18px; margin-bottom:8px;">
                        <span class="evidence-source-tag">[{s.get('source_id_label')}]</span>
                        <strong style="margin-left:8px; color:#F4F7FF;">{s.get('identifier')}</strong>
                        <span style="color:#A6B2C8; font-size:0.82rem; margin-left:12px;">({s.get('source_type')}) — {s.get('page_or_section')}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with tab_timeline:
            st.markdown("### **ReAct Agent Activity Log & Tool Calls**")
            timeline_events = res.get("timeline", [])
            if not timeline_events:
                st.info("No timeline records available.")
            else:
                for evt in timeline_events:
                    icon = "✅" if evt.status == "completed" else "⚠️" if evt.status == "warning" else "⏳"
                    tool_html = f"<div class='timeline-tool-tag'>Tool: {evt.tool_name} → {evt.tool_result_summary}</div>" if evt.tool_name else ""
                    st.markdown(
                        f"""
                        <div class="timeline-event-card">
                            <div class="timeline-event-header">
                                <span>{icon} {evt.agent_name}</span>
                                <span style="font-size:0.75rem; color:#A6B2C8;">{evt.action}</span>
                            </div>
                            <div class="timeline-event-detail">{evt.details}</div>
                            {tool_html}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        with tab_export:
            st.markdown("### 📥 **Export & Share Briefing**")
            md_path = st.session_state.report_service.export_markdown(
                res["report_markdown"],
                f"ARX_Research_{res.get('session_id', 'report')[:8]}.md"
            )
            pdf_path = st.session_state.report_service.export_pdf(
                res["report_markdown"],
                f"ARX_Research_{res.get('session_id', 'report')[:8]}.pdf"
            )

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    "📄 Download Markdown (.md)",
                    data=res["report_markdown"],
                    file_name=f"ARX_Research_{res.get('session_id', 'report')[:8]}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with col_d2:
                if pdf_path.exists():
                    st.download_button(
                        "📕 Download Executive PDF (.pdf)",
                        data=pdf_path.read_bytes(),
                        file_name=f"ARX_Research_{res.get('session_id', 'report')[:8]}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

            st.markdown("#### **Markdown Preview Snippet**")
            st.code(res["report_markdown"][:1200] + "\n\n...[Full report available in download]", language="markdown")

# ============================================================
# 4. DOCUMENT LIBRARY
# ============================================================
elif st.session_state.nav_radio == "Document Library":
    st.markdown("## 📚 **Document Library & RAG Corpus**")
    st.caption("Manage uploaded documents, view indexing status, and inspect extracted page content in ChromaDB.")

    # Upload Section
    with st.expander("📤 **Upload New Reference Document**", expanded=False):
        uploaded_doc = st.file_uploader(
            "Upload reference files (PDF, TXT, MD):",
            type=["pdf", "txt", "md"],
            key="library_file_uploader"
        )
        if uploaded_doc is not None:
            save_path = settings.UPLOADS_DIR / uploaded_doc.name
            save_path.write_bytes(uploaded_doc.getbuffer())
            
            # Immediately parse and ingest into ChromaDB
            with st.spinner(f"Parsing and indexing {uploaded_doc.name}..."):
                reader = DocumentReaderTool()
                read_res = reader.read_document(save_path)
                if read_res["success"]:
                    rag = RAGRetrieverTool()
                    ingest_res = rag.ingest_document(
                        document_name=uploaded_doc.name,
                        pages=read_res["pages"],
                        source_id=f"DOC_{uploaded_doc.name[:4]}",
                        session_id="global"
                    )
                    st.success(f"✅ Ingested {uploaded_doc.name}: {read_res['total_pages']} pages, {ingest_res.get('chunks_created', 0)} chunks indexed into ChromaDB.")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to parse: {read_res.get('error')}")

    # Gather all existing documents
    sample_files = list(settings.SAMPLE_DOCS_DIR.glob("*.*"))
    upload_files = list(settings.UPLOADS_DIR.glob("*.*"))
    all_files = [(f, "sample") for f in sample_files] + [(f, "uploaded") for f in upload_files]

    # Search & Filter
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        doc_search_query = st.text_input("🔍 Search Documents", placeholder="Filter by document name...")
    with col_filter:
        doc_type_filter = st.selectbox("Format Filter", ["All Formats", ".pdf", ".txt", ".md"], index=0)

    filtered_files = []
    for f, origin in all_files:
        if doc_search_query and doc_search_query.lower() not in f.name.lower():
            continue
        if doc_type_filter != "All Formats" and f.suffix.lower() != doc_type_filter:
            continue
        filtered_files.append((f, origin))

    st.markdown(f"**Indexed Documents ({len(filtered_files)}):**")

    if not filtered_files:
        st.markdown(
            render_empty_state("📁", "No Documents Found", "No documents match the specified search query or format filter."),
            unsafe_allow_html=True
        )
    else:
        reader = DocumentReaderTool()
        for f, origin in filtered_files:
            file_size_kb = f.stat().st_size / 1024
            origin_badge = "SAMPLE BENCHMARK" if origin == "sample" else "USER CORPUS"
            badge_class = "badge-inference" if origin == "sample" else "badge-supported"

            with st.expander(f"📄 {f.name} ({file_size_kb:.1f} KB) — {origin_badge}", expanded=False):
                col_d_info, col_d_action = st.columns([3, 1])
                with col_d_info:
                    doc_res = reader.read_document(f)
                    if doc_res["success"]:
                        st.markdown(
                            f"""
                            - **Total Pages:** {doc_res['total_pages']}
                            - **Total Characters:** {doc_res['total_characters']}
                            - **Extension:** <code>{f.suffix}</code>
                            - **File Location:** <code>{origin}</code>
                            """
                        )
                        if doc_res["pages"]:
                            st.text_area(
                                "Page 1 Content Preview",
                                doc_res["pages"][0]["text"][:1000],
                                height=120,
                                key=f"prev_{f.name}"
                            )
                    else:
                        st.error(f"Error reading file: {doc_res.get('error')}")

                with col_d_action:
                    if origin == "uploaded":
                        st.markdown("<p style='font-size:0.75rem; color:#A6B2C8;'>Manage Corpus:</p>", unsafe_allow_html=True)
                        if st.button("🗑️ Delete Document", key=f"del_doc_{f.name}"):
                            try:
                                f.unlink()
                                st.success(f"Deleted {f.name}")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error deleting: {str(ex)}")

# ============================================================
# 5. EVIDENCE EXPLORER
# ============================================================
elif st.session_state.nav_radio == "Evidence Explorer":
    st.markdown("## 📜 **Evidence Explorer**")
    st.caption("Inspect and audit verified factual claims recorded across research sessions in this workspace.")

    # Retrieve all evidence claims for workspace
    workspace_evidence = st.session_state.persist_mem.get_all_workspace_evidence(st.session_state.workspace_id)

    # Filter controls
    col_ef1, col_ef2 = st.columns([2, 1])
    with col_ef1:
        ev_search = st.text_input("🔍 Search Claims", placeholder="Filter by claim text or topic...")
    with col_ef2:
        ev_filter_status = st.selectbox(
            "Classification Status",
            ["All Classifications", "Supported", "Partial", "Conflicting", "Inference", "Insufficient"],
            index=0
        )

    filtered_evidence = []
    for ev in workspace_evidence:
        if ev_search and ev_search.lower() not in ev.get("claim", "").lower():
            continue
        if ev_filter_status != "All Classifications":
            if ev_filter_status.lower() not in ev.get("support_status", "supported").lower():
                continue
        filtered_evidence.append(ev)

    st.markdown(f"**Verified Evidence Items ({len(filtered_evidence)}):**")

    if not filtered_evidence:
        st.markdown(
            render_empty_state("📜", "No Evidence Claims Found", "Execute research inquiries to populate the verified evidence repository."),
            unsafe_allow_html=True
        )
    else:
        for ev in filtered_evidence:
            st.markdown(
                render_evidence_card(
                    claim=ev.get("claim", ""),
                    support_status=ev.get("support_status", "supported"),
                    passage_text=ev.get("passage_text", ""),
                    source_label=ev.get("source_id_label", "S1"),
                    doc_name=ev.get("session_title", "Research Session"),
                    page_num=ev.get("page_number", 1),
                    confidence=ev.get("confidence_score", 1.0)
                ),
                unsafe_allow_html=True
            )

# ============================================================
# 6. RESEARCH HISTORY
# ============================================================
elif st.session_state.nav_radio == "Research History":
    st.markdown("## 🗄️ **Research History & Workspace Memory**")
    st.caption(f"Persistent SQLite research repository isolated to Workspace: `{st.session_state.workspace_id}`")

    sessions = st.session_state.persist_mem.list_sessions(st.session_state.workspace_id)

    col_h_ctrl1, col_h_ctrl2 = st.columns([2, 1])
    with col_h_ctrl2:
        if st.button("🗑️ Clear Workspace Memory", help="Deletes all stored research sessions for this workspace"):
            st.session_state.persist_mem.clear_workspace_memory(st.session_state.workspace_id)
            st.success("Workspace memory cleared.")
            st.rerun()

    if not sessions:
        st.markdown(
            render_empty_state("🗄️", "Workspace History Empty", "No previous research sessions recorded in this workspace. Start an investigation in the Dashboard."),
            unsafe_allow_html=True
        )
    else:
        for s in sessions:
            with st.container():
                st.markdown(
                    f"""
                    <div class="premium-card" style="margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0; color:#F4F7FF;">{s['title']}</h4>
                            <span class="badge-epistemic badge-supported">{s['status'].upper()}</span>
                        </div>
                        <p style="color:#A6B2C8; font-size:0.86rem; margin:8px 0 4px 0;">
                            <strong>Inquiry:</strong> {s['research_question']}<br>
                            <strong>Timestamp:</strong> <code>{s['created_at']}</code>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                col_b1, col_b2 = st.columns([1, 4])
                with col_b1:
                    if st.button("Load Briefing", key=f"hist_view_{s['id']}"):
                        s_detail = st.session_state.persist_mem.get_session(s["id"], st.session_state.workspace_id)
                        if s_detail and s_detail.get("reports"):
                            st.session_state.latest_result = {
                                "session_id": s["id"],
                                "title": s["title"],
                                "report_markdown": s_detail["reports"][0]["report_markdown"],
                                "citation_score": s_detail["reports"][0]["citation_score"],
                                "sources": s_detail.get("sources", []),
                                "passages": [],
                                "claims": s_detail.get("evidence", []),
                                "contradictions": s_detail.get("contradictions", []),
                                "timeline": []
                            }
                            st.session_state.nav_radio = "Research Results"
                            st.rerun()
                with col_b2:
                    if st.button("Delete Session", key=f"hist_del_{s['id']}"):
                        st.session_state.persist_mem.delete_session(s["id"], st.session_state.workspace_id)
                        st.success("Session deleted.")
                        st.rerun()

# ============================================================
# 7. EVALUATION & TESTING
# ============================================================
elif st.session_state.nav_radio == "Evaluation & Testing":
    st.markdown("## 🧪 **Evaluation & Automated Testing Suite**")
    st.caption("Execute the 8 mandatory test cases and verification guardrails directly from the browser.")

    st.markdown(
        """
        <div class="premium-card">
            <h4 style="margin-top:0; color:#5B8CFF;">Mandatory System Verification Cases</h4>
            <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:10px; font-size:0.86rem; color:#CBD5E1;">
                <div><b>✓ Test 1:</b> Normal research request with relevant documents</div>
                <div><b>✓ Test 2:</b> Missing or blank research question validation</div>
                <div><b>✓ Test 3:</b> Contradictory information detection (35% vs 48%)</div>
                <div><b>✓ Test 4:</b> Empty retrieval honesty (zero evidence handling)</div>
                <div><b>✓ Test 5:</b> Invalid or corrupted PDF file rejection</div>
                <div><b>✓ Test 6:</b> Search provider timeout & network resilience</div>
                <div><b>✓ Test 7:</b> Nonexistent citation ID detection [S99]</div>
                <div><b>✓ Test 8:</b> SQLite workspace isolation between users</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("▶️ Run Automated Test Suite (Pytest)", use_container_width=True):
        with st.spinner("Executing pytest evaluation suite..."):
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-v"],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True
            )
            st.markdown("### **Execution Results**")
            if proc.returncode == 0:
                st.success("🎉 All evaluation test cases passed successfully!")
            else:
                st.warning("⚠️ Some tests reported issues or warnings.")

            st.code(proc.stdout, language="bash")

# ============================================================
# 8. API CONFIGURATION
# ============================================================
elif st.session_state.nav_radio == "API Configuration":
    st.markdown("## 🔑 **API Configuration & Provider Status**")
    st.caption("Inspect Google Gemini, OpenAI, and Anthropic Claude credentials and trigger live connection tests.")

    p_info = st.session_state.providers.get_provider_details()

    for p_key, p_val in p_info.items():
        with st.container():
            stat = p_val["status"]
            badge_class = "badge-supported" if stat == ProviderStatus.CONNECTED else "badge-partial" if stat == ProviderStatus.CONFIGURED else "badge-conflicting"

            st.markdown(
                f"""
                <div class="premium-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#F4F7FF;">{p_val['name']}</h3>
                        <span class="badge-epistemic {badge_class}">{p_val['status'].upper()}</span>
                    </div>
                    <p style="color:#A6B2C8; font-size:0.86rem; margin:8px 0 4px 0;">
                        <strong>System Role:</strong> {p_val['role']}<br>
                        <strong>Model ID:</strong> <code>{p_val['model']}</code><br>
                        <strong>Configured Key:</strong> <code>{p_val['masked_key']}</code>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_test, col_msg = st.columns([1, 3])
            with col_test:
                if st.button(f"Test {p_val['name'].split()[0]} Connection", key=f"api_test_{p_key}"):
                    with st.spinner(f"Pinging {p_val['name']}..."):
                        if p_key == "gemini":
                            ok, msg = st.session_state.providers.test_gemini_connection()
                        elif p_key == "openai":
                            ok, msg = st.session_state.providers.test_openai_connection()
                        elif p_key == "anthropic":
                            ok, msg = st.session_state.providers.test_anthropic_connection()

                        if ok:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
                        st.rerun()

# ============================================================
# 9. SETTINGS
# ============================================================
elif st.session_state.nav_radio == "Settings":
    st.markdown("## ⚙️ **System Settings**")
    st.caption("Runtime parameters, storage directories, and agent limits.")

    st.markdown(
        f"""
        <div class="premium-card">
            <h4 style="margin-top:0; color:#5B8CFF;">Active Configuration</h4>
            <div style="font-size:0.88rem; color:#CBD5E1; line-height:1.7;">
                • <b>Data Directory:</b> <code>{settings.DATA_DIR}</code><br>
                • <b>Uploads Directory:</b> <code>{settings.UPLOADS_DIR}</code><br>
                • <b>ChromaDB Vector Store:</b> <code>{settings.CHROMA_PERSIST_DIR}</code><br>
                • <b>SQLite Database:</b> <code>{settings.DATABASE_PATH}</code><br>
                • <b>RAG Chunk Size:</b> <code>{settings.CHUNK_SIZE}</code> characters (Overlap: <code>{settings.CHUNK_OVERLAP}</code>)<br>
                • <b>Embedding Model:</b> <code>{settings.EMBEDDING_MODEL_NAME}</code><br>
                • <b>Top-K Retrieved Chunks:</b> <code>{settings.TOP_K_CHUNKS}</code><br>
                • <b>Min Similarity Score:</b> <code>{settings.MIN_SIMILARITY_SCORE}</code><br>
                • <b>Max Tool Iterations:</b> <code>{settings.MAX_ITERATIONS}</code><br>
                • <b>Execution Timeout:</b> <code>{settings.EXECUTION_TIMEOUT_SECONDS}s</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
