"""
ARX INVENTOR - Evaluation Suite: Memory & Workspace Isolation Tests
Validates strict user/workspace separation, data-retention controls, and persistence lifecycle.
"""

import pytest
from pathlib import Path
from memory.persistent_memory import PersistentMemory

@pytest.fixture
def memory_instance(tmp_path):
    db_path = tmp_path / "memory_isolation_test.db"
    return PersistentMemory(db_path=db_path)

def test_8_persistent_memory_isolation_between_two_users_workspaces(memory_instance):
    """
    Test Case 8: Persistent memory isolation between two users/workspaces.
    Ensures that records created in Workspace A are invisible and inaccessible to Workspace B.
    """
    mem = memory_instance

    # 1. User Alpha in Workspace A creates research session
    session_a = mem.create_session(
        workspace_id="user_alpha_workspace",
        title="Alpha Research: Hydrogen Fuel Cells",
        research_question="What is the round-trip efficiency of green hydrogen fuel cells?",
        scope_config={"audience": "engineer", "depth": "detailed"}
    )
    mem.save_sources(session_a, [{
        "source_id_label": "S1",
        "title": "Alpha Confidential Document",
        "identifier": "alpha_doc.pdf"
    }])
    mem.save_report(session_a, "# Alpha Report Content", citation_score=1.0)

    # 2. User Beta in Workspace B creates research session
    session_b = mem.create_session(
        workspace_id="user_beta_workspace",
        title="Beta Research: Quantum Computing",
        research_question="What are topological superconductors?",
        scope_config={"audience": "physicist", "depth": "basic"}
    )

    # Verify Workspace Alpha sessions
    alpha_sessions = mem.list_sessions(workspace_id="user_alpha_workspace")
    assert len(alpha_sessions) == 1
    assert alpha_sessions[0]["id"] == session_a
    assert alpha_sessions[0]["title"] == "Alpha Research: Hydrogen Fuel Cells"

    # Verify Workspace Beta sessions (must NOT see Alpha's session)
    beta_sessions = mem.list_sessions(workspace_id="user_beta_workspace")
    assert len(beta_sessions) == 1
    assert beta_sessions[0]["id"] == session_b
    assert beta_sessions[0]["title"] == "Beta Research: Quantum Computing"
    assert all(s["id"] != session_a for s in beta_sessions), "User Beta must not see User Alpha's session"

    # Verify direct get_session enforces workspace parameter
    alpha_from_beta = mem.get_session(session_id=session_a, workspace_id="user_beta_workspace")
    assert alpha_from_beta is None, "Accessing Alpha's session using Beta's workspace ID must return None"

    # Verify data retention / deletion isolation
    mem.delete_session(session_id=session_a, workspace_id="user_alpha_workspace")
    assert len(mem.list_sessions("user_alpha_workspace")) == 0
    # Beta session must remain intact
    assert len(mem.list_sessions("user_beta_workspace")) == 1
