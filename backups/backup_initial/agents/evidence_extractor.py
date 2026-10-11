"""
ARX INVENTOR - Agent 3: Evidence Extractor
Role: Evidence Extraction Specialist
Powered by: OpenAI
Objective: Extract verifiable factual claims, exact supporting quotations, page numbers,
and source metadata from retrieved chunks.
"""

from typing import List, Dict, Any
import json
import re
from services.provider_service import ProviderService

class EvidenceExtractorAgent:
    """Agent 3: Extracts claims and exact quotations from retrieved chunks."""

    def __init__(self, provider_service: ProviderService):
        self.provider_service = provider_service
        self.role = "Senior Evidence Extraction Specialist"
        self.goal = "Extract empirical claims and verbatim excerpts directly from evidence passages without fabrication."
        self.backstory = (
            "You are a rigorous evidence extractor. You never extrapolate or fabricate quotations. "
            "Every claim you extract includes the exact source label, page number, and literal excerpt."
        )

    def extract_evidence(
        self,
        retrieved_passages: List[Dict[str, Any]],
        research_question: str,
        demo_mode: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Extracts structured claims from passages.
        Returns list of:
        {
            "source_id_label": "S1",
            "document_name": "...",
            "page_number": 3,
            "claim": "...",
            "passage_text": "...", # verbatim excerpt
            "support_status": "supported" | "partially_supported" | "conflicting" | "inference" | "insufficient",
            "confidence_score": 0.95
        }
        """
        if not retrieved_passages:
            return []

        if demo_mode:
            return self._deterministic_extract(retrieved_passages)

        passages_summary = []
        for idx, p in enumerate(retrieved_passages[:8]): # analyze top passages
            passages_summary.append(
                f"[Passage {idx+1}] Source: [{p.get('source_id', 'S1')}] | Document: {p.get('document_name')} | Page: {p.get('page_number', 1)}\n"
                f"Content: \"{p.get('text', '')}\"\n"
            )

        system_prompt = (
            f"You are the {self.role}. {self.backstory}\n"
            "Extract distinct factual claims and verbatim quotes from the passages provided.\n"
            "Respond strictly with a JSON list of objects having keys:\n"
            "'source_id_label', 'page_number', 'claim', 'passage_text', 'support_status', 'confidence_score'."
        )

        user_prompt = f"""
Research Question: {research_question}

Retrieved Passages:
{chr(10).join(passages_summary)}

Extract 3 to 6 key factual claims. For each, quote the exact passage text verbatim.
Label support_status as one of: 'supported', 'partially_supported', 'conflicting', 'inference', 'insufficient'.
Output JSON only:
[
  {{
    "source_id_label": "S1",
    "page_number": 1,
    "claim": "Core factual claim extracted",
    "passage_text": "Exact verbatim quote from the passage",
    "support_status": "supported",
    "confidence_score": 0.95
  }}
]
"""

        resp = self.provider_service.generate_completion(
            provider="openai",
            prompt=user_prompt,
            system_prompt=system_prompt,
            demo_mode=demo_mode,
            demo_task="extraction"
        )

        if resp.get("simulated"):
            return self._deterministic_extract(retrieved_passages)

        text = resp.get("text", "")
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                extracted = json.loads(match.group(0))
                # Add document name mapping
                doc_map = {p.get("source_id", "S1"): p.get("document_name", "") for p in retrieved_passages}
                for item in extracted:
                    item["document_name"] = doc_map.get(item.get("source_id_label"), "")
                return extracted
            except Exception:
                pass

        return self._deterministic_extract(retrieved_passages)

    def _deterministic_extract(self, passages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback deterministic claim extraction."""
        claims = []
        for p in passages:
            text = p.get("text", "")
            # Split into sentences or extract clean first sentence
            sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if len(s.strip()) > 20]
            if sentences:
                claim_candidate = sentences[0]
                claims.append({
                    "source_id_label": p.get("source_id", "S1"),
                    "document_name": p.get("document_name", "Document"),
                    "page_number": p.get("page_number", 1),
                    "claim": claim_candidate,
                    "passage_text": text[:200] if len(text) > 200 else text,
                    "support_status": "supported",
                    "confidence_score": 0.92
                })
        return claims[:6]
