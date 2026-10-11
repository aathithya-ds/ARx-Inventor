"""
ARX INVENTOR - Tool A: Document Reader
Extracts clean text and page metadata from PDF, TXT, and Markdown documents.
Enforces file format, size validations, and prompt-injection safety sanitization.
"""

from typing import List, Dict, Any
from pathlib import Path
import re
from config.settings import settings

class DocumentReaderTool:
    """Safely parses documents and extracts structured page-level text."""

    def __init__(self, max_size_mb: int = settings.MAX_FILE_SIZE_MB):
        self.max_size_mb = max_size_mb
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS

    def read_document(self, file_path: str | Path) -> Dict[str, Any]:
        """
        Reads and validates a document.
        Returns:
        {
            "success": bool,
            "filename": str,
            "extension": str,
            "total_pages": int,
            "pages": [{"page_number": int, "text": str}],
            "total_characters": int,
            "error": str | None
        }
        """
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "filename": path.name,
                "extension": path.suffix.lower(),
                "total_pages": 0,
                "pages": [],
                "total_characters": 0,
                "error": f"File does not exist: {path}"
            }

        # Validate file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_size_mb:
            return {
                "success": False,
                "filename": path.name,
                "extension": path.suffix.lower(),
                "total_pages": 0,
                "pages": [],
                "total_characters": 0,
                "error": f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed limit of {self.max_size_mb} MB"
            }

        # Validate extension
        ext = path.suffix.lower()
        if ext not in self.allowed_extensions:
            return {
                "success": False,
                "filename": path.name,
                "extension": ext,
                "total_pages": 0,
                "pages": [],
                "total_characters": 0,
                "error": f"Unsupported file type '{ext}'. Supported types: {', '.join(self.allowed_extensions)}"
            }

        # Parse based on extension
        try:
            if ext == ".pdf":
                return self._read_pdf(path)
            elif ext in (".txt", ".md"):
                return self._read_text_file(path)
            else:
                return {
                    "success": False,
                    "filename": path.name,
                    "extension": ext,
                    "total_pages": 0,
                    "pages": [],
                    "total_characters": 0,
                    "error": f"Unsupported extension: {ext}"
                }
        except Exception as e:
            return {
                "success": False,
                "filename": path.name,
                "extension": ext,
                "total_pages": 0,
                "pages": [],
                "total_characters": 0,
                "error": f"Corrupted or unreadable file: {str(e)}"
            }

    def _read_pdf(self, path: Path) -> Dict[str, Any]:
        """Reads a PDF with pypdf and extracts pages."""
        try:
            from pypdf import PdfReader
        except ImportError:
            return {
                "success": False,
                "filename": path.name,
                "extension": ".pdf",
                "total_pages": 0,
                "pages": [],
                "total_characters": 0,
                "error": "pypdf library not installed"
            }

        try:
            reader = PdfReader(str(path))
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    return {
                        "success": False,
                        "filename": path.name,
                        "extension": ".pdf",
                        "total_pages": 0,
                        "pages": [],
                        "total_characters": 0,
                        "error": "PDF is password encrypted and cannot be parsed"
                    }

            pages = []
            total_chars = 0
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                cleaned = self._sanitize_evidence_text(page_text)
                if cleaned:
                    pages.append({
                        "page_number": idx + 1,
                        "text": cleaned
                    })
                    total_chars += len(cleaned)

            if not pages:
                return {
                    "success": False,
                    "filename": path.name,
                    "extension": ".pdf",
                    "total_pages": len(reader.pages),
                    "pages": [],
                    "total_characters": 0,
                    "error": "PDF contains no extractable text (may be image-only/scanned document)"
                }

            return {
                "success": False if total_chars == 0 else True,
                "filename": path.name,
                "extension": ".pdf",
                "total_pages": len(reader.pages),
                "pages": pages,
                "total_characters": total_chars,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "filename": path.name,
                "extension": ".pdf",
                "total_pages": 0,
                "pages": [],
                "total_characters": 0,
                "error": f"Failed to read PDF file: {str(e)}"
            }

    def _read_text_file(self, path: Path) -> Dict[str, Any]:
        """Reads a plain text or markdown file."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        content = None
        for enc in encodings:
            try:
                content = path.read_text(encoding=enc)
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            return {
                "success": False,
                "filename": path.name,
                "extension": path.suffix.lower(),
                "total_pages": 0,
                "pages": [],
                "total_characters": 0,
                "error": "Failed to decode text file with standard encodings"
            }

        cleaned = self._sanitize_evidence_text(content)
        pages = [{"page_number": 1, "text": cleaned}]
        return {
            "success": True,
            "filename": path.name,
            "extension": path.suffix.lower(),
            "total_pages": 1,
            "pages": pages,
            "total_characters": len(cleaned),
            "error": None
        }

    def _sanitize_evidence_text(self, text: str) -> str:
        """
        Guardrail: Sanitizes untrusted document text.
        Neutralizes potential prompt injection markers and stripping script tags.
        """
        # Neutralize system prompt overrides or jailbreak attempts
        injection_patterns = [
            r"ignore (all )?previous instructions",
            r"system prompt override",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
            r"<\|endoftext\|>",
        ]
        sanitized = text
        for pat in injection_patterns:
            sanitized = re.sub(pat, "[FILTERED_INSTRUCTION_MARKER]", sanitized, flags=re.IGNORECASE)

        # Strip control characters except newline and tab
        sanitized = "".join(ch for ch in sanitized if ch in ("\n", "\r", "\t") or ch.isprintable())
        return sanitized.strip()
