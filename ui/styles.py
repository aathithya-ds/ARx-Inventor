"""
ARX INVENTOR - Design System & Styles
Linear & Notion inspired SaaS aesthetic for verifiable AI research.
"""

def get_custom_css() -> str:
    """Returns the comprehensive CSS stylesheet for ARX INVENTOR."""
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ============================================================
   DESIGN TOKENS & ROOT VARIABLES
   ============================================================ */
:root {
    --bg-main: #0B1020;
    --bg-sidebar: #0E1528;
    --bg-surface: #141D32;
    --bg-elevated: #19243B;
    --bg-card-hover: #1E2B46;
    --border-subtle: #28344C;
    --border-focus: #5B8CFF;
    --accent-blue: #5B8CFF;
    --accent-blue-hover: #4A7AE8;
    --accent-blue-glow: rgba(91, 140, 255, 0.18);
    --accent-violet: #8B7CFF;
    --accent-violet-glow: rgba(139, 124, 255, 0.16);
    --text-primary: #F4F7FF;
    --text-secondary: #A6B2C8;
    --text-muted: #64748B;
    
    /* Semantic Status Colors */
    --status-success: #10B981;
    --status-success-bg: rgba(16, 185, 129, 0.12);
    --status-success-border: rgba(16, 185, 129, 0.35);
    
    --status-warning: #F59E0B;
    --status-warning-bg: rgba(245, 158, 11, 0.12);
    --status-warning-border: rgba(245, 158, 11, 0.35);
    
    --status-danger: #F43F5E;
    --status-danger-bg: rgba(244, 63, 94, 0.12);
    --status-danger-border: rgba(244, 63, 94, 0.35);
    
    --status-info: #38BDF8;
    --status-info-bg: rgba(56, 189, 248, 0.12);
    --status-info-border: rgba(56, 189, 248, 0.35);
    
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 18px;
    --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.45);
    --shadow-elevated: 0 10px 30px -5px rgba(0, 0, 0, 0.6);
}

/* ============================================================
   GLOBAL RESET & TYPOGRAPHY
   ============================================================ */
html, body, .stApp {
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    letter-spacing: -0.011em;
}

/* Header container cleanup */
header[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: blur(12px) !important;
}

/* Fix main content padding */
.main .block-container {
    max-width: 1380px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: var(--bg-main);
}
::-webkit-scrollbar-thumb {
    background: var(--border-subtle);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--accent-blue);
}

/* ============================================================
   SIDEBAR STYLING
   ============================================================ */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
}

/* Sidebar Brand Header */
.arx-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 18px;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border-subtle);
}

.arx-brand-icon {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-violet) 100%);
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px var(--accent-blue-glow);
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
}

.arx-brand-text {
    display: flex;
    flex-direction: column;
}

.arx-brand-title {
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--text-primary);
    line-height: 1.2;
}

.arx-brand-sub {
    font-size: 0.72rem;
    color: var(--text-secondary);
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

/* Sidebar Navigation Radio Buttons */
[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: var(--radius-sm) !important;
    padding: 8px 12px !important;
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease-in-out !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    margin-bottom: 0 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border-color: rgba(91, 140, 255, 0.25) !important;
    transform: translateX(2px);
}

[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(90deg, rgba(91, 140, 255, 0.16) 0%, rgba(139, 124, 255, 0.08) 100%) !important;
    border: 1px solid var(--accent-blue) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px var(--accent-blue-glow) !important;
}

/* Hide standard radio dot inside sidebar navigation */
[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
    display: none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label div:first-child {
    display: none !important;
}

/* ============================================================
   TOP NAVIGATION BAR / HEADER
   ============================================================ */
.top-nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 18px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    margin-bottom: 24px;
    box-shadow: var(--shadow-card);
}

.breadcrumbs {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.breadcrumb-root {
    color: var(--text-muted);
    font-weight: 500;
}

.breadcrumb-sep {
    color: var(--border-subtle);
}

.breadcrumb-current {
    color: var(--text-primary);
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}

.nav-badges-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    color: var(--text-secondary);
}

.nav-status-pill.pill-live {
    background: var(--status-success-bg);
    border-color: var(--status-success-border);
    color: var(--status-success);
}

.nav-status-pill.pill-demo {
    background: rgba(139, 124, 255, 0.14);
    border-color: rgba(139, 124, 255, 0.35);
    color: var(--accent-violet);
}

.nav-pulse-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: currentColor;
    box-shadow: 0 0 6px currentColor;
}

/* ============================================================
   HERO BANNER
   ============================================================ */
.arx-hero {
    position: relative;
    background: linear-gradient(135deg, rgba(20, 29, 50, 0.85) 0%, rgba(25, 36, 59, 0.7) 100%);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 32px 36px;
    margin-bottom: 28px;
    overflow: hidden;
    box-shadow: var(--shadow-card);
}

.arx-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 450px;
    height: 450px;
    background: radial-gradient(circle, rgba(91, 140, 255, 0.12) 0%, transparent 70%);
    pointer-events: none;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: rgba(91, 140, 255, 0.1);
    border: 1px solid rgba(91, 140, 255, 0.28);
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--accent-blue);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.hero-title {
    font-size: 2.15rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.18;
    color: var(--text-primary);
    margin: 0 0 10px 0;
}

.hero-title .gradient-text {
    background: linear-gradient(135deg, #7BB0FF 0%, #B4A2FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-description {
    font-size: 0.96rem;
    color: var(--text-secondary);
    line-height: 1.55;
    max-width: 780px;
    margin: 0;
}

/* ============================================================
   STAT SUMMARY METRICS CARDS
   ============================================================ */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}

@media (max-width: 900px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

.stat-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    transition: all 0.2s ease;
    box-shadow: var(--shadow-card);
}

.stat-card:hover {
    border-color: rgba(91, 140, 255, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
}

.stat-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.stat-card-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.stat-card-icon {
    width: 28px;
    height: 28px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    font-size: 0.85rem;
    color: var(--accent-blue);
}

.stat-card-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
    font-family: 'JetBrains Mono', monospace;
}

.stat-card-subtext {
    font-size: 0.75rem;
    color: var(--text-muted);
}

/* ============================================================
   CONTAINERS & CARDS
   ============================================================ */
.premium-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 22px 24px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-card);
    transition: border-color 0.2s ease;
}

.premium-card:hover {
    border-color: rgba(91, 140, 255, 0.3);
}

.premium-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(40, 52, 76, 0.6);
}

.card-title-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.card-subtitle {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin: 0;
}

/* ============================================================
   AGENT WORKFLOW CARDS (6 AGENTS)
   ============================================================ */
.agent-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
    width: 100%;
    box-sizing: border-box;
}

@media (max-width: 768px) {
    .agent-grid {
        grid-template-columns: 1fr;
    }
}


.agent-node {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    position: relative;
    transition: all 0.2s ease;
}

.agent-node.status-active {
    border-color: var(--accent-blue);
    background: linear-gradient(135deg, var(--bg-surface) 0%, rgba(91, 140, 255, 0.08) 100%);
    box-shadow: 0 0 16px rgba(91, 140, 255, 0.15);
}

.agent-node.status-completed {
    border-color: rgba(16, 185, 129, 0.4);
}

.agent-node-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.agent-role-pill {
    display: flex;
    align-items: center;
    gap: 8px;
}

.agent-icon-box {
    width: 28px;
    height: 28px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.88rem;
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
}

.agent-node.status-active .agent-icon-box {
    background: rgba(91, 140, 255, 0.15);
    border-color: var(--accent-blue);
    color: var(--accent-blue);
}

.agent-node.status-completed .agent-icon-box {
    background: var(--status-success-bg);
    border-color: var(--status-success-border);
    color: var(--status-success);
}

.agent-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-primary);
}

.agent-model-tag {
    font-size: 0.7rem;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', monospace;
}

.agent-desc {
    font-size: 0.77rem;
    color: var(--text-secondary);
    line-height: 1.4;
}

.agent-state-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 8px;
    border-radius: 9999px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.agent-state-idle {
    background: var(--bg-elevated);
    color: var(--text-muted);
    border: 1px solid var(--border-subtle);
}

.agent-state-running {
    background: rgba(91, 140, 255, 0.15);
    color: var(--accent-blue);
    border: 1px solid var(--accent-blue);
}

.agent-state-completed {
    background: var(--status-success-bg);
    color: var(--status-success);
    border: 1px solid var(--status-success-border);
}

/* ============================================================
   EVIDENCE & EPISTEMIC CLASSIFICATION CARDS
   ============================================================ */
.evidence-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    margin-bottom: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: all 0.2s ease;
}

.evidence-card:hover {
    border-color: rgba(91, 140, 255, 0.4);
    background: var(--bg-card-hover);
}

.evidence-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.evidence-claim {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.4;
}

.evidence-quote {
    background: var(--bg-elevated);
    border-left: 3px solid var(--accent-blue);
    padding: 10px 14px;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    font-size: 0.85rem;
    color: #CBD5E1;
    font-style: italic;
    line-height: 1.5;
    margin: 4px 0;
}

.evidence-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.77rem;
    color: var(--text-secondary);
}

.evidence-source-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 7px;
    background: rgba(91, 140, 255, 0.12);
    border: 1px solid rgba(91, 140, 255, 0.3);
    border-radius: var(--radius-sm);
    color: var(--accent-blue);
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

/* Epistemic Status Badges */
.badge-epistemic {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 9px;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.badge-supported {
    background: var(--status-success-bg);
    border: 1px solid var(--status-success-border);
    color: var(--status-success);
}

.badge-partial {
    background: var(--status-warning-bg);
    border: 1px solid var(--status-warning-border);
    color: var(--status-warning);
}

.badge-conflicting {
    background: var(--status-danger-bg);
    border: 1px solid var(--status-danger-border);
    color: var(--status-danger);
}

.badge-inference {
    background: rgba(139, 124, 255, 0.14);
    border: 1px solid rgba(139, 124, 255, 0.35);
    color: var(--accent-violet);
}

.badge-insufficient {
    background: rgba(100, 116, 139, 0.16);
    border: 1px solid rgba(100, 116, 139, 0.35);
    color: var(--text-secondary);
}

/* ============================================================
   CONTRADICTION ANALYSIS CARD
   ============================================================ */
.contradiction-card {
    background: linear-gradient(135deg, rgba(20, 29, 50, 0.95) 0%, rgba(35, 18, 30, 0.45) 100%);
    border: 1px solid rgba(244, 63, 94, 0.4);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.contradiction-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.contradiction-title {
    font-size: 0.98rem;
    font-weight: 700;
    color: #FDA4AF;
    display: flex;
    align-items: center;
    gap: 8px;
}

.contradiction-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

@media (max-width: 768px) {
    .contradiction-split {
        grid-template-columns: 1fr;
    }
}

.contradiction-side {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 12px;
}

.side-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 4px;
}

.reconciliation-box {
    background: rgba(11, 16, 32, 0.8);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    font-size: 0.86rem;
    color: var(--text-primary);
    line-height: 1.5;
}

/* ============================================================
   DOCUMENT LIBRARY CARD
   ============================================================ */
.doc-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.2s ease;
}

.doc-card:hover {
    border-color: rgba(91, 140, 255, 0.35);
    background: var(--bg-card-hover);
}

.doc-info-group {
    display: flex;
    align-items: center;
    gap: 14px;
}

.doc-icon-badge {
    width: 38px;
    height: 38px;
    border-radius: var(--radius-sm);
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    color: var(--accent-blue);
}

.doc-name {
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 3px;
}

.doc-meta {
    font-size: 0.77rem;
    color: var(--text-secondary);
    display: flex;
    gap: 12px;
}

/* ============================================================
   BUTTONS STYLING
   ============================================================ */
/* Primary Buttons */
div.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue) 0%, #4F46E5 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: var(--radius-md) !important;
    padding: 10px 22px !important;
    box-shadow: 0 4px 14px var(--accent-blue-glow) !important;
    transition: all 0.2s ease-in-out !important;
    letter-spacing: -0.01em !important;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, var(--accent-blue-hover) 0%, #4338CA 100%) !important;
    box-shadow: 0 6px 20px rgba(91, 140, 255, 0.35) !important;
    transform: translateY(-1px) !important;
}

div.stButton > button:active {
    transform: translateY(1px) !important;
}

/* Secondary & Ghost buttons inside expanders/cards */
button[kind="secondary"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    box-shadow: none !important;
}
button[kind="secondary"]:hover {
    border-color: var(--accent-blue) !important;
    background: var(--bg-surface) !important;
}

/* ============================================================
   INPUT FIELDS, SELECTBOXES & TEXTAREAS
   ============================================================ */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-size: 0.9rem !important;
    padding: 10px 14px !important;
    transition: all 0.15s ease !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px var(--accent-blue-glow) !important;
}

[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}

/* Label styling */
[data-testid="stWidgetLabel"] p {
    color: var(--text-secondary) !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    margin-bottom: 4px !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background: var(--bg-surface) !important;
    border: 1px dashed var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent-blue) !important;
}

/* ============================================================
   TABS STYLING
   ============================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px !important;
    background-color: var(--bg-surface) !important;
    padding: 6px !important;
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border-subtle) !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 8px 16px !important;
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background-color: var(--bg-elevated) !important;
}

.stTabs [aria-selected="true"] {
    background-color: var(--accent-blue) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px var(--accent-blue-glow) !important;
}

/* ============================================================
   EXPANDERS & CALLOUTS
   ============================================================ */
[data-testid="stExpander"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    margin-bottom: 12px !important;
}

[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
}

[data-testid="stExpander"] summary:hover {
    color: var(--accent-blue) !important;
}

/* Timeline Activity Event */
.timeline-event-card {
    border-left: 2px solid var(--accent-blue);
    padding: 10px 14px;
    margin-bottom: 12px;
    background: var(--bg-surface);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.timeline-event-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-primary);
}

.timeline-event-detail {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

.timeline-tool-tag {
    display: inline-block;
    margin-top: 4px;
    padding: 2px 8px;
    background: rgba(139, 124, 255, 0.12);
    border: 1px solid rgba(139, 124, 255, 0.3);
    border-radius: var(--radius-sm);
    color: var(--accent-violet);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
}

/* Empty States */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    background: var(--bg-surface);
    border: 1px dashed var(--border-subtle);
    border-radius: var(--radius-lg);
    margin: 20px 0;
}

.empty-state-icon {
    font-size: 2.2rem;
    margin-bottom: 10px;
    opacity: 0.7;
}

.empty-state-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 6px;
}

.empty-state-desc {
    font-size: 0.84rem;
    color: var(--text-secondary);
    max-width: 440px;
    margin: 0 auto;
}

/* ============================================================
   ANIMATIONS & MICRO-INTERACTIONS (SMOOTH & PROFESSIONAL)
   ============================================================ */

/* 1. Pulse Glow for Live & Demo Mode Indicators */
@keyframes pulseDotGlow {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        transform: scale(1.15);
        box-shadow: 0 0 0 7px rgba(16, 185, 129, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

.nav-status-pill.pill-live .nav-pulse-dot {
    animation: pulseDotGlow 2.2s infinite cubic-bezier(0.4, 0, 0.6, 1);
}

@keyframes pulseVioletGlow {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(139, 124, 255, 0.7);
    }
    70% {
        transform: scale(1.15);
        box-shadow: 0 0 0 7px rgba(139, 124, 255, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(139, 124, 255, 0);
    }
}

.nav-status-pill.pill-demo .nav-pulse-dot {
    animation: pulseVioletGlow 2.2s infinite cubic-bezier(0.4, 0, 0.6, 1);
}

/* 2. Ambient Radial Glow Drift for Hero Section */
@keyframes ambientDrift {
    0% {
        transform: translate(0, 0) scale(1);
        opacity: 0.7;
    }
    50% {
        transform: translate(-35px, 25px) scale(1.2);
        opacity: 0.95;
    }
    100% {
        transform: translate(0, 0) scale(1);
        opacity: 0.7;
    }
}

.arx-hero::before {
    animation: ambientDrift 14s ease-in-out infinite !important;
}

/* 3. Brand Icon Breathing & Micro-Tilt */
@keyframes brandPulse {
    0%, 100% {
        box-shadow: 0 4px 14px rgba(91, 140, 255, 0.28);
    }
    50% {
        box-shadow: 0 6px 22px rgba(139, 124, 255, 0.45);
    }
}

.arx-brand-icon {
    animation: brandPulse 5s ease-in-out infinite;
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease !important;
}

.arx-brand:hover .arx-brand-icon {
    transform: scale(1.08) rotate(4deg) !important;
    box-shadow: 0 8px 24px rgba(91, 140, 255, 0.55) !important;
}

/* 4. Fluid Card Entrance Animation */
@keyframes cardEntrance {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.top-nav-bar, .arx-hero, .stat-card, .premium-card, .agent-node, .evidence-card, .contradiction-card {
    animation: cardEntrance 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* 5. Stat Cards Hover Lifts & Icon Physics */
.stat-card {
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.25s ease,
                box-shadow 0.25s ease !important;
}

.stat-card:hover {
    transform: translateY(-4px) !important;
    border-color: rgba(91, 140, 255, 0.5) !important;
    box-shadow: 0 12px 28px -4px rgba(0, 0, 0, 0.55), 0 0 16px rgba(91, 140, 255, 0.2) !important;
}

.stat-card:hover .stat-card-icon {
    transform: scale(1.15) rotate(4deg);
    background: rgba(91, 140, 255, 0.2);
    border-color: var(--accent-blue);
    color: #FFFFFF;
}

.stat-card-icon {
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), 
                background 0.25s ease, 
                border-color 0.25s ease, 
                color 0.25s ease !important;
}

/* 6. Agent Nodes Hover Lifts & Running Aura */
.agent-node {
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.25s ease,
                box-shadow 0.25s ease,
                background 0.25s ease !important;
}

.agent-node:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(91, 140, 255, 0.45) !important;
    background: var(--bg-card-hover) !important;
    box-shadow: 0 8px 24px -2px rgba(0, 0, 0, 0.45), 0 0 12px rgba(91, 140, 255, 0.15) !important;
}

.agent-node:hover .agent-icon-box {
    transform: scale(1.12);
    color: var(--accent-blue);
}

.agent-icon-box {
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), color 0.2s ease !important;
}

@keyframes activeAgentAura {
    0%, 100% {
        border-color: var(--accent-blue);
        box-shadow: 0 0 14px rgba(91, 140, 255, 0.22);
    }
    50% {
        border-color: #8B7CFF;
        box-shadow: 0 0 24px rgba(139, 124, 255, 0.38);
    }
}

.agent-node.status-active {
    animation: activeAgentAura 3s ease-in-out infinite !important;
}

@keyframes badgeRunningPulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.75;
        transform: scale(0.96);
    }
}

.agent-state-running {
    animation: badgeRunningPulse 1.8s ease-in-out infinite !important;
}

/* 7. Button Hover Shimmer & Click Physics */
div.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue) 0%, #4F46E5 50%, #7C3AED 100%) !important;
    background-size: 200% 100% !important;
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div.stButton > button:hover {
    background-position: 100% 0 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(91, 140, 255, 0.4) !important;
}

div.stButton > button:active {
    transform: translateY(1px) scale(0.98) !important;
    box-shadow: 0 2px 10px rgba(91, 140, 255, 0.25) !important;
}

/* 8. Evidence Cards Hover Micro-Lift */
.evidence-card {
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.2s ease,
                box-shadow 0.2s ease,
                background 0.2s ease !important;
}

.evidence-card:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(91, 140, 255, 0.45) !important;
    box-shadow: 0 8px 22px -2px rgba(0, 0, 0, 0.4) !important;
}

.badge-epistemic {
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

.badge-epistemic:hover {
    transform: scale(1.05) !important;
}

/* 9. Sidebar Navigation Smooth Slide Hover */
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    transform: translateX(4px) !important;
}
</style>

"""
