"""
ARX INVENTOR - Evaluation Suite: Research Workflow Tests
Validates standard research pipelines, contradiction detection, and empty retrieval honesty.
"""

import pytest
from pathlib import Path
from services.research_service import ResearchService
from memory.session_memory import SessionMemory
from memory.persistent_memory import PersistentMemory
from services.provider_service import ProviderService

@pytest.fixture
def clean_services(tmp_path):
    """Provides isolated memory and service instances for tests."""
    db_file = tmp_path / "test_arx.db"
    p_mem = PersistentMemory(db_path=db_file)
    s_mem = SessionMemory(workspace_id="test_workspace")
    providers = ProviderService()
    svc = ResearchService(
        session_memory=s_mem,
        persistent_memory=p_mem,
        provider_service=providers
    )
    return svc, tmp_path

def test_1_normal_research_request_with_relevant_documents(clean_services):
    """
    Test Case 1: Normal research request with relevant documents.
    Verifies that documents are ingested, RAG passages retrieved, claims extracted,
    and report generated with verifiable citations.
    """
    svc, tmp_path = clean_services
    doc_path = Path("sample_documents/Solar_Energy_Outlook_Report_A.txt")
    assert doc_path.exists(), "Sample document A must exist"

    question = "What was the Global Solar Adoption rate in 2024?"
    scope_config = {
        "target_audience": "analyst",
        "research_depth": "standard",
        "report_length": "medium",
        "enable_web_search": False,
        "source_priority": "documents_first"
    }

    result = svc.execute_research_workflow(
        research_question=question,
        scope_config=scope_config,
        uploaded_file_paths=[doc_path],
        workspace_id="test_workspace",
        demo_mode=True
    )

    assert result["session_id"] is not None
    assert len(result["sources"]) >= 1
    assert len(result["passages"]) >= 1
    assert len(result["claims"]) >= 1
    assert "35%" in result["report_markdown"]
    assert "[S1]" in result["report_markdown"]
    assert result["citation_score"] >= 0.80

def test_3_two_documents_containing_contradictory_information(clean_services):
    """
    Test Case 3: Two documents containing contradictory information (35% vs 48%).
    Confirms that both figures are preserved, cited with respective sources,
    and marked as unresolved/methodologically distinct.
    """
    svc, tmp_path = clean_services
    doc_a = Path("sample_documents/Solar_Energy_Outlook_Report_A.txt")
    doc_b = Path("sample_documents/Solar_Energy_Outlook_Report_B.txt")

    assert doc_a.exists() and doc_b.exists()

    question = "What was the global solar market adoption rate and valuation in 2024?"
    scope_config = {
        "target_audience": "analyst",
        "research_depth": "comprehensive",
        "report_length": "detailed",
        "enable_web_search": False,
        "source_priority": "documents_first"
    }

    result = svc.execute_research_workflow(
        research_question=question,
        scope_config=scope_config,
        uploaded_file_paths=[doc_a, doc_b],
        workspace_id="test_workspace",
        demo_mode=True
    )

    # Verify both sources registered
    assert len(result["sources"]) >= 2
    # Verify contradiction was detected
    assert len(result["contradictions"]) >= 1

    contradiction_item = result["contradictions"][0]
    assert "percentage" in contradiction_item["metric_or_topic"].lower()

    report_md = result["report_markdown"]
    # Both conflicting percentages must be preserved in the briefing
    assert "35%" in report_md
    assert "48%" in report_md
    # Report must discuss the contradiction
    assert "Contradiction Case" in report_md or "Disagreements and Contradictory Evidence" in report_md

def test_4_research_question_with_no_supporting_evidence(clean_services):
    """
    Test Case 4: Research question with no supporting evidence.
    Confirms that empty retrieval produces an explicit evidence-gap message
    and refuses to fabricate unsupported claims.
    """
    svc, tmp_path = clean_services
    doc_path = Path("sample_documents/Solar_Energy_Outlook_Report_A.txt")

    unrelated_question = "What is the quantum coherence time of trapped ion qubits in absolute vacuum?"
    scope_config = {
        "target_audience": "researcher",
        "research_depth": "basic",
        "report_length": "short",
        "enable_web_search": False,
        "source_priority": "documents_first"
    }

    # When querying with strict similarity threshold, no chunks should match
    result = svc.execute_research_workflow(
        research_question=unrelated_question,
        scope_config=scope_config,
        uploaded_file_paths=[], # No uploaded quantum docs
        workspace_id="test_workspace",
        demo_mode=True
    )

    report_md = result["report_markdown"]
    assert "EVIDENTIARY GAP NOTICE" in report_md or "Insufficient evidence" in report_md
    assert "no relevant evidence" in report_md.lower() or "zero-evidence" in report_md.lower()
