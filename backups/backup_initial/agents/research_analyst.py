"""
ARX INVENTOR - Agent 4: Research Analyst
Role: Comparative Research Analyst & Contradiction Detective
Objective: Compare claims across retrieved documents and web sources,
detect agreements, disagreements, numerical discrepancies, and evidentiary gaps.
"""

from typing import List, Dict, Any
import re
from services.provider_service import ProviderService

class ResearchAnalystAgent:
    """Agent 4: Identifies cross-source agreements, contradictions, and evidentiary gaps."""

    def __init__(self, provider_service: ProviderService):
        self.provider_service = provider_service
        self.role = "Senior Comparative Research Analyst"
        self.goal = "Scrutinize claims across independent sources to identify consensus, evaluate methodological nuance, and spotlight unresolved contradictions."
        self.backstory = (
            "You are an analytical evaluator who specializes in forensic evidence comparison. "
            "When sources disagree (e.g., 35% vs 48%), you never discard or hide either claim; "
            "you cite both, scrutinize differences in scope, population, or methodology, and determine "
            "if the disparity is reconcilable or must remain marked as unresolved."
        )

    def analyze_evidence_and_contradictions(
        self,
        claims: List[Dict[str, Any]],
        research_question: str,
        demo_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Conducts comparative analysis and detects contradictions.
        Returns:
        {
            "agreements": list[dict],
            "contradictions": list[dict], # Structured contradiction items
            "evidence_gaps": list[str],
            "source_limitations": list[str]
        }
        """
        # Run rule-based numerical/claim contradiction detector first
        detected_contradictions = self._detect_numerical_contradictions(claims)

        agreements = []
        evidence_gaps = []
        source_limitations = []

        if not claims:
            return {
                "agreements": [],
                "contradictions": [],
                "evidence_gaps": [
                    "Zero supporting claims retrieved from available documents or web sources.",
                    "Unable to verify primary research question due to absence of grounded evidence."
                ],
                "source_limitations": ["Corpus lacks relevant data on the inquiry."]
            }

        # Check for agreements across different sources
        by_source: Dict[str, List[Dict[str, Any]]] = {}
        for c in claims:
            s_label = c.get("source_id_label", "S1")
            by_source.setdefault(s_label, []).append(c)

        if len(by_source) > 1:
            agreements.append({
                "topic": "Multi-source coverage",
                "finding": f"Retrieved independent claims across {len(by_source)} distinct sources.",
                "sources_cited": list(by_source.keys())
            })
        else:
            source_limitations.append("All retrieved evidence originates from a single source; multi-source triangulation is limited.")

        if not detected_contradictions:
            # Check for general disagreements
            if len(claims) >= 2:
                agreements.append({
                    "topic": "General consensus",
                    "finding": "Retrieved sources demonstrate consistent trajectory without direct metric disputes.",
                    "sources_cited": list(by_source.keys())
                })
        else:
            source_limitations.append(
                f"Identified {len(detected_contradictions)} conflicting metric claims across documents."
            )

        evidence_gaps.append("Long-term historical trend data prior to measurement periods was not fully specified.")

        return {
            "agreements": agreements,
            "contradictions": detected_contradictions,
            "evidence_gaps": evidence_gaps,
            "source_limitations": source_limitations
        }

    def _detect_numerical_contradictions(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Forensic rule-based detector for divergent percentages, currency metrics, or statistics
        between distinct source documents.
        """
        contradictions = []

        # Extract percentages and dollar metrics
        metrics_by_source: List[Dict[str, Any]] = []
        for c in claims:
            text = f"{c.get('claim', '')} {c.get('passage_text', '')}"
            src = c.get("source_id_label", "S1")
            doc = c.get("document_name", "")

            # Percentages pattern: e.g. 35%, 48.5%
            pcts = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
            for p in pcts:
                metrics_by_source.append({
                    "type": "percentage",
                    "value": float(p),
                    "raw": f"{p}%",
                    "source": src,
                    "doc": doc,
                    "claim": c.get("claim", "") or text[:120],
                    "text": text
                })

            # Dollar figures: e.g. $320B, $450 billion
            dollars = re.findall(r'\$\s*(\d+(?:\.\d+)?)\s*(?:[BMK]|billion|million)?', text, re.IGNORECASE)
            for d in dollars:
                metrics_by_source.append({
                    "type": "currency",
                    "value": float(d),
                    "raw": f"${d}",
                    "source": src,
                    "doc": doc,
                    "claim": c.get("claim", "") or text[:120],
                    "text": text
                })

        # Compare metrics of same type across differing sources
        for i in range(len(metrics_by_source)):
            for j in range(i + 1, len(metrics_by_source)):
                m1 = metrics_by_source[i]
                m2 = metrics_by_source[j]

                # Must be different sources and same metric type
                if m1["source"] != m2["source"] and m1["type"] == m2["type"]:
                    # If numerical values differ significantly (> 5% difference)
                    diff = abs(m1["value"] - m2["value"])
                    if diff > 1.0:
                        # Extract topic words
                        words1 = set(re.findall(r'\w{4,}', m1["text"].lower()))
                        words2 = set(re.findall(r'\w{4,}', m2["text"].lower()))
                        shared_keywords = words1.intersection(words2)

                        topic = f"Discrepancy in {m1['type']} estimates ({m1['raw']} vs {m2['raw']})"
                        if shared_keywords:
                            topic += f" regarding {', '.join(list(shared_keywords)[:3])}"

                        contradiction_item = {
                            "metric_or_topic": topic,
                            "source_a_label": m1["source"],
                            "claim_a": f"[{m1['source']}] ({m1['doc']}): Reports {m1['raw']} — '{m1['claim']}'",
                            "source_b_label": m2["source"],
                            "claim_b": f"[{m2['source']}] ({m2['doc']}): Reports {m2['raw']} — '{m2['claim']}'",
                            "reconciliation_analysis": (
                                f"Source [{m1['source']}] asserts {m1['raw']}, whereas Source [{m2['source']}] asserts {m2['raw']}. "
                                "Disparity likely arises from differences in scope boundary, survey sample, decentralized vs centralized accounting, "
                                "or distinct measurement methodologies. The figures cannot be arbitrarily blended without direct methodological reconciliation."
                            ),
                            "status": "unresolved"
                        }

                        # Check if duplicate
                        is_dup = any(
                            c["metric_or_topic"] == contradiction_item["metric_or_topic"]
                            for c in contradictions
                        )
                        if not is_dup:
                            contradictions.append(contradiction_item)

        return contradictions
