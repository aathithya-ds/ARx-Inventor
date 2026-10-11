"""
ARX INVENTOR - Evaluation Suite: Citation & Hallucination Tests
Validates citation resolution, phantom source detection, and quotation authenticity.
"""

import pytest
from tools.citation_validator import CitationValidatorTool

@pytest.fixture
def validator():
    return CitationValidatorTool()

@pytest.fixture
def sample_evidence():
    sources = [
        {"source_id_label": "S1", "identifier": "report_a.pdf", "title": "Report A"},
        {"source_id_label": "S2", "identifier": "report_b.pdf", "title": "Report B"}
    ]
    passages = [
        {"source_id": "S1", "page_number": 2, "text": "Global Solar Adoption reached 35% of total renewable capacity additions in 2024."},
        {"source_id": "S2", "page_number": 5, "text": "Decentralized solar microgrids generated over $450B in combined market capitalization."}
    ]
    return sources, passages

def test_7_invalid_citation_or_nonexistent_source_id(validator, sample_evidence):
    """
    Test Case 7: Invalid citation or nonexistent source ID.
    Confirms that citation validator flags [S99] or missing IDs and marks report invalid.
    """
    sources, passages = sample_evidence

    # Report containing hallucinated citation [S99]
    report_with_invalid_citation = """
    ## Key Findings
    Solar adoption reached unprecedented levels in 2024 [S1].
    Additionally, advanced fusion reactors were deployed commercially [S99].
    """

    results = validator.validate_report(
        report_markdown=report_with_invalid_citation,
        retrieved_sources=sources,
        retrieved_passages=passages
    )

    assert not results["valid"], "Report with phantom citations must be rejected"
    assert "S99" in results["missing_source_ids"]
    assert any("nonexistent source" in issue.lower() for issue in results["flagged_issues"])

def test_authentic_citations_pass_validation(validator, sample_evidence):
    """
    Checks that correctly grounded citations and exact quotations receive high score.
    """
    sources, passages = sample_evidence

    valid_report = """
    # Solar Briefing
    ## Executive Summary
    The investigation synthesized key findings [S1].
    ## Key Findings
    - Solar adoption reached 35% in 2024 [S1].
    - As reported: "Global Solar Adoption reached 35% of total renewable capacity additions in 2024." [S1]
    - Decentralized energy market valuation reached $450B [S2].
    """

    results = validator.validate_report(
        report_markdown=valid_report,
        retrieved_sources=sources,
        retrieved_passages=passages
    )

    assert results["valid"] is True
    assert results["citation_score"] >= 0.85
    assert len(results["missing_source_ids"]) == 0

def test_fabricated_quotation_is_flagged(validator, sample_evidence):
    """
    Checks that fabricated or hallucinated quotes not found in source text are flagged.
    """
    sources, passages = sample_evidence

    hallucinated_quote_report = """
    ## Key Findings
    The report states: "All fossil fuels will be permanently banned by the United Nations in 2025" [S1].
    """

    results = validator.validate_report(
        report_markdown=hallucinated_quote_report,
        retrieved_sources=sources,
        retrieved_passages=passages
    )

    assert any("Quoted passage not found" in issue for issue in results["flagged_issues"])
    unverified = [q for q in results["quotes_checked"] if q["status"] == "UNVERIFIED_QUOTE"]
    assert len(unverified) >= 1
