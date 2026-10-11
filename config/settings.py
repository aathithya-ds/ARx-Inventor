"""
ARX INVENTOR - Configuration Settings
Manages environment variables, provider keys, model IDs, file paths, and research limits.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CHROMA_PERSIST_DIR = DATA_DIR / "chroma_db"
DATABASE_PATH = DATA_DIR / "arx_memory.db"
REPORTS_DIR = BASE_DIR / "reports"
SAMPLE_DOCS_DIR = BASE_DIR / "sample_documents"

# Ensure runtime directories exist
for directory in [DATA_DIR, UPLOADS_DIR, CHROMA_PERSIST_DIR, REPORTS_DIR, SAMPLE_DOCS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Load .env file
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)
class Settings:
    """Central configuration class for ARX INVENTOR."""
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    CHROMA_PERSIST_DIR: Path = CHROMA_PERSIST_DIR
    DATABASE_PATH: Path = DATABASE_PATH
    REPORTS_DIR: Path = REPORTS_DIR
    SAMPLE_DOCS_DIR: Path = SAMPLE_DOCS_DIR

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
    
    # Model Identifiers
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022").strip()
    
    # Operational Flags
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    DEFAULT_WORKSPACE_ID: str = os.getenv("DEFAULT_WORKSPACE_ID", "default_workspace").strip()
    
    # RAG Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "600"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "120"))
    TOP_K_CHUNKS: int = int(os.getenv("TOP_K_CHUNKS", "5"))
    MIN_SIMILARITY_SCORE: float = float(os.getenv("MIN_SIMILARITY_SCORE", "0.20"))
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # Web Search & Security Guardrails
    SEARCH_TIMEOUT: int = int(os.getenv("SEARCH_TIMEOUT", "10"))
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
    ALLOWED_EXTENSIONS: tuple = (".pdf", ".txt", ".md")
    
    # Agent & Execution Limits
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))
    MAX_TOOL_CALLS: int = int(os.getenv("MAX_TOOL_CALLS", "15"))
    EXECUTION_TIMEOUT_SECONDS: int = int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "180"))
    MAX_TOKENS_PER_AGENT: int = int(os.getenv("MAX_TOKENS_PER_AGENT", "4096"))
    
    # Excluded Domains Guardrail (Default Blocklist)
    DEFAULT_EXCLUDED_DOMAINS: list = [
        "localhost", "127.0.0.1", "0.0.0.0", "internal", "local",
        "pinterest.com", "tiktok.com", "instagram.com"
    ]

settings = Settings()
