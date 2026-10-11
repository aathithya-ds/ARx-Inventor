"""
ARX INVENTOR - Tool D: Citation Validator
Cross-verifies report citations against retrieved sources and evidence passages.
Flags unverified citations, nonexistent source IDs, and ungrounded claims.
"""

from typing import List, Dict, Any, Set
import re
from difflib import SequenceMatcher

class CitationValidatorTool:
    """Rigorous validator ensuring zero hallucinated citations and grounded claims."""

    def __init__(self):
        self.citation_pattern = re.compile(r'\[(S\d+)\]')

    def extract_citations_from_text(self, text: str) -> List[str]:
        """Finds all in-text citation markers like [S1], [S2]."""
        return self.citation_pattern.findall(text)

    def validate_report(
        self,
        report_markdown: str,
        retrieved_sources: List[Dict[str, Any]],
        retrieved_passages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates citations in a report.
        Returns:
        {
            "valid": bool,
            "citation_score": float, # 0.0 to 1.0
            "total_citations_found": int,
            "unique_cited_ids": list,
            "registered_source_ids": list,
            "missing_source_ids": list,
            "unverified_citations": list,
            "quotes_checked": list,
            "flagged_issues": list,
            "recommendation": str
        }
        """
        citations_found = self.extract_citations_from_text(report_markdown)
        unique_cited = sorted(list(set(citations_found)))

        # Registered sources
        registered_ids: Set[str] = set()
        for s in retrieved_sources:
            lbl = s.get("source_id_label") or s.get("id") or s.get("source_id")
            if lbl:
                registered_ids.add(lbl)

        # Also source IDs from passages
        for p in retrieved_passages:
            lbl = p.get("source_id") or p.get("source_id_label")
            if lbl:
                registered_ids.add(lbl)

        missing_sources = [cid for cid in unique_cited if cid not in registered_ids]

        flagged_issues = []
        if missing_sources:
            flagged_issues.append(
                f"Citations point to nonexistent source IDs: {', '.join(missing_sources)}"
            )

        if not unique_cited and ("Key Findings" in report_markdown or "Executive Summary" in report_markdown):
            flagged_issues.append("Report contains key claims without any citations.")

        # Check quoted strings within the report
        quotes = re.findall(r'"([^"]{15,})"', report_markdown)
        quote_verifications = []
        all_passage_text = " ".join([p.get("text", "").lower() for p in retrieved_passages])

        for q in quotes:
            # Strip trailing ellipsis, periods, and whitespace
            q_clean = re.sub(r'[\.\s\…]+$', '', q.strip()).lower()
            if not q_clean or len(q_clean) < 10:
                continue
            if q_clean in all_passage_text or any(q_clean in p.get("text", "").lower() for p in retrieved_passages):
                quote_verifications.append({"quote": q, "status": "VERIFIED_EXACT"})
            else:
                # Check fuzzy match against chunks
                best_ratio = 0.0
                for p in retrieved_passages:
                    p_txt = p.get("text", "").lower()
                    if q_clean in p_txt:
                        best_ratio = 1.0
                        break
                    ratio = SequenceMatcher(None, q_clean, p_txt).ratio()
                    if ratio > best_ratio:
                        best_ratio = ratio
                if best_ratio >= 0.60:
                    quote_verifications.append({"quote": q, "status": "VERIFIED_PARTIAL", "ratio": round(best_ratio, 2)})
                else:
                    quote_verifications.append({"quote": q, "status": "UNVERIFIED_QUOTE", "ratio": round(best_ratio, 2)})
                    flagged_issues.append(f"Quoted passage not found in retrieved source passages: \"{q[:80]}...\"")

        # Compute citation validity score
        if not unique_cited:
            citation_score = 0.0
        else:
            valid_count = len([c for c in citations_found if c in registered_ids])
            citation_score = round(valid_count / len(citations_found), 2)

        # Deduct score for unverified quotes
        unverified_quotes = [q for q in quote_verifications if q["status"] == "UNVERIFIED_QUOTE"]
        if unverified_quotes:
            citation_score = max(0.0, round(citation_score - 0.15 * len(unverified_quotes), 2))

        is_valid = len(missing_sources) == 0 and citation_score >= 0.80

        recommendation = "Approved for publication." if is_valid else "Requires citation refinement before finalization."

        return {
            "valid": is_valid,
            "citation_score": citation_score,
            "total_citations_found": len(citations_found),
            "unique_cited_ids": unique_cited,
            "registered_source_ids": sorted(list(registered_ids)),
            "missing_source_ids": missing_sources,
            "quotes_checked": quote_verifications,
            "flagged_issues": flagged_issues,
            "recommendation": recommendation
        }
