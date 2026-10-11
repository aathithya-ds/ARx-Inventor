"""
ARX INVENTOR - Evaluation Suite: Failure Modes & Guardrail Tests
Validates missing inputs, corrupt file handling, network timeouts, and SSRF security guardrails.
"""

import pytest
from pathlib import Path
from services.research_service import ResearchService
from tools.document_reader import DocumentReaderTool
from tools.approved_web_search import ApprovedWebSearchTool

def test_2_missing_research_question():
    """
    Test Case 2: Missing or blank research question.
    Ensures system halts early with helpful validation error without calling agents.
    """
    svc = ResearchService()
    valid, msg = svc.validate_inputs("")
    assert not valid
    assert "cannot be empty" in msg.lower()

    valid_short, short_msg = svc.validate_inputs("what")
    assert not valid_short
    assert "too short" in short_msg.lower()

def test_5_invalid_or_corrupted_pdf():
    """
    Test Case 5: Invalid or corrupted PDF file.
    Confirms DocumentReaderTool gracefully catches corruption and returns structured error.
    """
    reader = DocumentReaderTool()
    corrupt_file = Path("sample_documents/corrupted_dummy.pdf")
    assert corrupt_file.exists()

    result = reader.read_document(corrupt_file)
    assert result["success"] is False
    assert result["total_pages"] == 0
    assert result["error"] is not None
    assert "corrupt" in result["error"].lower() or "failed" in result["error"].lower() or "cannot" in result["error"].lower()

def test_6_search_provider_timeout_or_api_failure():
    """
    Test Case 6: Search provider timeout or network failure.
    Validates that ApprovedWebSearchTool catches timeouts gracefully without crashing.
    """
    # Tool configured with tiny timeout
    search_tool = ApprovedWebSearchTool(timeout=1)
    
    # Attempting to fetch non-routable / dropping IP or simulated error
    res = search_tool.fetch_webpage_content("http://192.0.2.1") # TEST-NET address that will drop/time out or get rejected
    assert res["success"] is False
    assert res["error"] is not None

def test_security_guardrail_blocks_localhost_and_private_ips():
    """
    SSRF Security Guardrail:
    Confirms that localhost, 127.0.0.1, internal networks, and unapproved schemes are blocked.
    """
    search_tool = ApprovedWebSearchTool(
        allowed_domains=["example.com"],
        excluded_domains=["banned-site.com"]
    )

    # 1. Localhost
    safe_local, reason_local = search_tool.is_url_safe("http://localhost:8501/admin")
    assert not safe_local
    assert "prohibited" in reason_local.lower() or "not in the allowed" in reason_local.lower() or "matches excluded" in reason_local.lower()

    # 2. Loopback IP
    safe_ip, reason_ip = search_tool.is_url_safe("http://127.0.0.1:8000/secret")
    assert not safe_ip

    # 3. Excluded domain
    safe_excl, reason_excl = search_tool.is_url_safe("https://banned-site.com/article")
    assert not safe_excl
    assert "matches excluded domain" in reason_excl.lower() or "not in the allowed" in reason_excl.lower()

    # 4. Invalid protocol
    safe_proto, reason_proto = search_tool.is_url_safe("file:///etc/passwd")
    assert not safe_proto
    assert "scheme" in reason_proto.lower()
