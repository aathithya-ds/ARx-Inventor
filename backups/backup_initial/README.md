# ARX INVENTOR — Autonomous AI Research Assistant with Source-Based Briefing

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![CrewAI](https://img.shields.io/badge/orchestration-CrewAI-black.svg)](https://crewai.com/)
[![Tests](https://img.shields.io/badge/tests-11%2F11%20passing-brightgreen.svg)]()

**ARX INVENTOR** is an enterprise-grade AI research assistant website that accepts a research question, ingests documents and approved web sources, retrieves empirical evidence using ChromaDB vector search, performs forensic comparative analysis across sources to detect contradictory metrics, and generates a structured, 14-section source-grounded research briefing with traceable in-text citations (`[S1]`, `[S2]`).

---

## 🌟 Key Features

1. **Multi-Agent Orchestration (CrewAI)**:
   - **Agent 1: Research Planner (Google Gemini)** — Inquiry deconstruction, scope definition, and investigative subquestions.
   - **Agent 2: Source Retriever** — Multi-source semantic vector retrieval and permitted web search with allowlist/blocklist enforcement.
   - **Agent 3: Evidence Extractor (OpenAI)** — Extraction of empirical claims, verbatim quotations, and exact page numbers.
   - **Agent 4: Research Analyst** — Comparative triangulation and automated contradiction detection (e.g., reconciling 35% vs 48% metric disparities).
   - **Agent 5: Synthesis Writer (OpenAI)** — Generates 14-section research briefings with explicit epistemic labels (`[Supported by evidence]`, `[Conflicting evidence]`, `[Inference]`, `[Insufficient evidence]`).
   - **Agent 6: Citation Quality Reviewer (Anthropic Claude)** — Rigorous citation audit, quotation verification against literal passage text, and compliance scoring.

2. **Real RAG & Multi-Format Parsing**:
   - Parses **PDF** (via PyPDF with page-level tracking), **TXT**, and **Markdown**.
   - Embeds text chunks into dense vector representations.
   - Vector storage and semantic cosine similarity querying via **ChromaDB**.

3. **Observable ReAct Activity Loop**:
   - Real-time step-by-step timeline displaying actual tool names, results summaries, item counts, and timestamps.
   - Guardrails against SSRF (blocks `localhost`, loopbacks, and private IPs) and prompt injections.

4. **Multi-Provider & Demo Simulation Mode**:
   - Supports Google Gemini, OpenAI, and Anthropic Claude independently.
   - Built-in **Demo Mode**: Allows exploring the application and running the entire automated test suite offline without requiring paid API keys.

5. **Persistent Workspace Memory**:
   - SQLite persistent storage isolated strictly by user/workspace identifier.
   - Stores research questions, plans, retrieved sources, evidence items, contradictions, and report versions.

6. **Interactive Citation Inspector & File Exports**:
   - Select any citation tag (`[S1]`, `[S2]`) to immediately inspect its origin document, page number, and literal excerpts.
   - One-click export to **Markdown (`.md`)** and **Executive PDF (`.pdf`)** styled via ReportLab.

---

## 🚀 Quickstart Guide (Windows Instructions)

### 1. Verify Python Installation
Ensure Python 3.11 or higher is installed:
```powershell
python --version
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to create your local `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and fill in your API keys (optional if using Demo Mode):
```env
# 1. Google Gemini (Used for Planning)
GEMINI_API_KEY=your_gemini_api_key_here

# 2. OpenAI (Used for Extraction & Synthesis)
OPENAI_API_KEY=your_openai_api_key_here

# 3. Anthropic Claude (Used for Citation Audit)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Runtime Settings
DEMO_MODE=false
DEFAULT_WORKSPACE_ID=default_user
```

### 5. Launch the Web Application
```powershell
streamlit run app.py
```
Open your browser and navigate to:
👉 **`http://localhost:8501`**

---

## 🧪 Running Automated Tests

ARX INVENTOR comes with an automated evaluation test suite covering all 8 mandatory evaluation criteria and safety checks:

```powershell
python -m pytest -v
```

### Test Cases Implemented:
| # | Test Name | File | Description |
|---|---|---|---|
| 1 | Normal Research Request | `tests/test_research.py` | Ingests documents, retrieves chunks, extracts claims, generates report with `[S1]`. |
| 2 | Missing Research Question | `tests/test_failures.py` | Halts early with friendly validation errors when query is empty. |
| 3 | Contradictory Information | `tests/test_research.py` | Compares Document A (35%) and Document B (48%), preserving and citing both figures. |
| 4 | No Supporting Evidence | `tests/test_research.py` | Returns an explicit evidentiary gap disclosure without hallucinating facts. |
| 5 | Corrupted / Invalid PDF | `tests/test_failures.py` | Handles corrupted PDFs gracefully with clean error dictionaries. |
| 6 | Search Timeout / Failure | `tests/test_failures.py` | Handles network errors and request timeouts without crashing. |
| 7 | Invalid Citation ID | `tests/test_citations.py` | Flags phantom citations like `[S99]` and deducts verification score. |
| 8 | Workspace Isolation | `tests/test_memory.py` | Proves User Alpha's research records are inaccessible to User Beta. |
| 9 | Grounded Quotation Audit | `tests/test_citations.py` | Confirms authentic quotations pass and fabricated quotes are flagged. |
| 10 | SSRF Security Guardrail | `tests/test_failures.py` | Blocks loopback, internal IPs (`127.0.0.1`), and excluded domains. |

You can also run these tests interactively from the web interface under the **"Evaluation & Testing"** navigation tab!

---

## 📂 Project Architecture

```
ARX-INVENTOR/
├── app.py                      # Main Streamlit web application & UI dashboard
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment configuration
├── .gitignore                  # Git ignore rules for keys and databases
├── pytest.ini                  # Pytest runner configuration
├── README.md                   # Complete documentation & Windows deployment guide
├── config/
│   ├── __init__.py
│   └── settings.py             # Central application configuration & thresholds
├── database/
│   ├── __init__.py
│   └── schema.py               # SQLite relational schema with workspace isolation
├── memory/
│   ├── __init__.py
│   ├── session_memory.py       # Live runtime state, timeline events & buffers
│   └── persistent_memory.py    # SQLite CRUD operations with workspace isolation
├── tools/
│   ├── __init__.py
│   ├── document_reader.py      # Multi-format parser (PDF, TXT, MD) with sanitization
│   ├── rag_retriever.py        # Vector ingestion and semantic retrieval tool
│   ├── approved_web_search.py  # DuckDuckGo search with domain filters & SSRF defense
│   └── citation_validator.py   # Grounded quote checker & citation mapper
├── rag/
│   ├── __init__.py
│   ├── chunking.py             # Overlapping text chunker with page tracking
│   ├── embeddings.py           # SentenceTransformer with resilient fallback
│   └── vector_store.py         # ChromaDB client & cosine similarity search
├── agents/
│   ├── __init__.py
│   ├── research_planner.py     # Agent 1: Research Planner (Gemini)
│   ├── source_retriever.py     # Agent 2: Source Retriever (RAG & Web tools)
│   ├── evidence_extractor.py   # Agent 3: Evidence Extractor (OpenAI)
│   ├── research_analyst.py     # Agent 4: Research Analyst & Contradiction Detective
│   ├── synthesis_writer.py     # Agent 5: Synthesis Writer (14-Section Briefing)
│   └── citation_reviewer.py    # Agent 6: Citation Quality Reviewer (Claude)
├── tasks/
│   ├── __init__.py
│   └── research_tasks.py       # CrewAI task specifications & prompt templates
├── services/
│   ├── __init__.py
│   ├── provider_service.py     # API key management, connection testing & simulation
│   ├── research_service.py     # Master orchestrator for the multi-agent workflow
│   └── report_service.py       # Markdown & ReportLab PDF export engine
├── sample_documents/           # Sample benchmarks including conflicting solar reports
├── tests/                      # Automated test suite (11 test cases)
└── reports/                    # Exported research reports (.md and .pdf)
```

---

## 🌐 Cloud Deployment (Streamlit Community Cloud)

1. Push this repository to GitHub:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit of ARX INVENTOR"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select **"Create app"** and point to your GitHub repository:
   - **Main file path:** `app.py`
4. In the App Settings under **"Secrets"**, add your API keys:
   ```toml
   GEMINI_API_KEY = "your_key"
   OPENAI_API_KEY = "your_key"
   ANTHROPIC_API_KEY = "your_key"
   DEMO_MODE = "false"
   ```
5. Click **Deploy!**

---

## 🛠️ Troubleshooting

- **Missing API Keys Warning**:
  Toggle **"Demo / Simulation Mode"** in the sidebar. This enables full exploration of the multi-agent workflow and report synthesis using verified facts without requiring active API subscriptions.
- **Port 8501 Already in Use**:
  Launch Streamlit on an alternate port:
  ```powershell
  streamlit run app.py --server.port 8502
  ```
- **Execution Policy Error in PowerShell**:
  If PowerShell blocks activating `.venv`, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
