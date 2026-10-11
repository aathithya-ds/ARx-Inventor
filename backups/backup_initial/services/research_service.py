"""
ARX INVENTOR - Research Service Orchestrator
Coordinates the 6-agent workflow, real ReAct tool loop, human approvals,
citation validation, observable activity timeline, and persistent memory.
"""

from typing import List, Dict, Any, Optional, Callable
import time
from pathlib import Path

from config.settings import settings
from memory.session_memory import SessionMemory
from memory.persistent_memory import PersistentMemory
from services.provider_service import ProviderService

from tools.document_reader import DocumentReaderTool
from tools.rag_retriever import RAGRetrieverTool
from tools.approved_web_search import ApprovedWebSearchTool
from tools.citation_validator import CitationValidatorTool

from agents.research_planner import ResearchPlannerAgent
from agents.source_retriever import SourceRetrieverAgent
from agents.evidence_extractor import EvidenceExtractorAgent
from agents.research_analyst import ResearchAnalystAgent
from agents.synthesis_writer import SynthesisWriterAgent
from agents.citation_reviewer import CitationReviewerAgent

class ResearchService:
    """Master orchestrator for ARX INVENTOR research executions."""

    def __init__(
        self,
        session_memory: Optional[SessionMemory] = None,
        persistent_memory: Optional[PersistentMemory] = None,
        provider_service: Optional[ProviderService] = None
    ):
        self.session_mem = session_memory or SessionMemory()
        self.persist_mem = persistent_memory or PersistentMemory()
        self.providers = provider_service or ProviderService()

        # Tools
        self.doc_reader = DocumentReaderTool()
        self.rag_tool = RAGRetrieverTool()
        self.web_search = ApprovedWebSearchTool()
        self.validator_tool = CitationValidatorTool()

        # Agents
        self.planner = ResearchPlannerAgent(self.providers)
        self.retriever = SourceRetrieverAgent(self.rag_tool, self.web_search)
        self.extractor = EvidenceExtractorAgent(self.providers)
        self.analyst = ResearchAnalystAgent(self.providers)
        self.writer = SynthesisWriterAgent(self.providers)
        self.reviewer = CitationReviewerAgent(self.providers, self.validator_tool)

    def validate_inputs(self, research_question: str) -> tuple[bool, str]:
        """Validates research query before starting execution."""
        cleaned = research_question.strip()
        if not cleaned:
            return False, "Research question cannot be empty. Please enter an investigation query."
        if len(cleaned) < 5:
            return False, "Research question is too short. Please provide a substantive query (at least 5 characters)."
        return True, "Valid input"

    def process_uploaded_documents(
        self,
        file_paths: List[str | Path],
        session_id: str,
        on_progress: Optional[Callable[[str, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Parses uploaded documents and indexes them in RAG storage.
        """
        ingested_sources = []
        source_counter = 1

        for fpath in file_paths:
            path = Path(fpath)
            if on_progress:
                on_progress("Document Reader", f"Parsing document: {path.name}")

            # Read document
            read_res = self.doc_reader.read_document(path)
            if not read_res["success"]:
                self.session_mem.add_timeline_event(
                    agent_name="Document Reader",
                    action=f"Failed to parse {path.name}",
                    status="warning",
                    details=read_res.get("error", "Unknown error"),
                    tool_name="DocumentReaderTool",
                    tool_result_summary="Error reading file"
                )
                continue

            source_label = f"S{source_counter}"
            source_counter += 1

            # Ingest to RAG
            ingest_res = self.rag_tool.ingest_document(
                document_name=path.name,
                pages=read_res["pages"],
                source_id=source_label,
                session_id=session_id
            )

            source_record = {
                "source_id_label": source_label,
                "source_type": "uploaded_document",
                "title": path.name,
                "identifier": path.name,
                "page_or_section": f"1 to {read_res['total_pages']} pages",
                "metadata": {
                    "total_pages": read_res["total_pages"],
                    "total_characters": read_res["total_characters"],
                    "chunks": ingest_res.get("chunks_created", 0)
                }
            }
            ingested_sources.append(source_record)
            self.session_mem.add_source(source_record)

            self.session_mem.add_timeline_event(
                agent_name="Document Ingestion",
                action=f"Indexed {path.name}",
                status="completed",
                details=f"Extracted {read_res['total_pages']} pages, indexed {ingest_res.get('chunks_created', 0)} chunks.",
                tool_name="RAGRetrieverTool",
                tool_result_summary=f"Success: {ingest_res.get('chunks_created', 0)} chunks stored"
            )

        return ingested_sources

    def generate_research_plan(
        self,
        research_question: str,
        scope_config: Dict[str, Any],
        available_documents: List[str],
        demo_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Agent 1: Generates structured research plan using Google Gemini.
        """
        self.session_mem.research_question = research_question
        self.session_mem.scope_config = scope_config

        self.session_mem.add_timeline_event(
            agent_name="Research Planner (Gemini)",
            action="Formulating research plan and subquestions",
            status="running",
            details="Analyzing inquiry scope and audience expectations."
        )

        plan = self.planner.plan_research(
            research_question=research_question,
            target_audience=scope_config.get("target_audience", "analyst"),
            research_depth=scope_config.get("research_depth", "standard"),
            report_length=scope_config.get("report_length", "medium"),
            source_priority=scope_config.get("source_priority", "documents_first"),
            available_documents=available_documents,
            web_search_enabled=scope_config.get("enable_web_search", False),
            additional_instructions=scope_config.get("additional_instructions", ""),
            demo_mode=demo_mode
        )

        self.session_mem.research_plan = plan
        self.session_mem.add_timeline_event(
            agent_name="Research Planner (Gemini)",
            action="Research plan created",
            status="completed",
            details=f"Formulated {len(plan.get('subquestions', []))} investigative subquestions."
        )

        return plan

    def execute_research_workflow(
        self,
        research_question: str,
        scope_config: Dict[str, Any],
        uploaded_file_paths: List[str | Path],
        workspace_id: str = "default_workspace",
        demo_mode: bool = False,
        on_progress: Optional[Callable[[str, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes the observable multi-agent research loop.
        """
        # 1. Validation
        valid, val_msg = self.validate_inputs(research_question)
        if not valid:
            raise ValueError(val_msg)

        # 2. Reset session & initialize database record
        self.session_mem.reset(workspace_id=workspace_id)
        session_id = self.persist_mem.create_session(
            workspace_id=workspace_id,
            title=f"Research: {research_question[:60]}",
            research_question=research_question,
            scope_config=scope_config
        )
        self.session_mem.session_id = session_id

        # 3. Document Ingestion
        if on_progress:
            on_progress("Document Ingestion", "Parsing and indexing uploaded documents...")
        doc_sources = self.process_uploaded_documents(
            uploaded_file_paths,
            session_id=session_id,
            on_progress=on_progress
        )

        # 4. Agent 1: Research Planning (Gemini)
        if on_progress:
            on_progress("Research Planner", "Gemini is structuring the research plan...")
        plan = self.generate_research_plan(
            research_question=research_question,
            scope_config=scope_config,
            available_documents=[s["title"] for s in doc_sources],
            demo_mode=demo_mode
        )
        self.persist_mem.update_session_plan(session_id, plan)

        # 5. Agent 2: Source Retrieval (RAG & Web Search Tools)
        if on_progress:
            on_progress("Source Retriever", "Executing RAG and search tools for evidence passages...")
        self.session_mem.add_timeline_event(
            agent_name="Source Retriever",
            action="Searching approved sources and retrieving passages",
            status="running",
            details="Querying ChromaDB vector index and approved web domains."
        )

        # Update web tool domain restrictions
        self.web_search.allowed_domains = scope_config.get("allowed_domains", [])
        self.web_search.excluded_domains = scope_config.get("excluded_domains", settings.DEFAULT_EXCLUDED_DOMAINS)

        retrieval_res = self.retriever.retrieve_for_subquestions(
            subquestions=plan.get("subquestions", [research_question]),
            session_id=session_id,
            enable_web_search=scope_config.get("enable_web_search", False),
            source_priority=scope_config.get("source_priority", "documents_first"),
            top_k=settings.TOP_K_CHUNKS
        )

        passages = retrieval_res["passages"]
        sources = retrieval_res["sources"]
        for s in sources:
            self.session_mem.add_source(s)
        self.session_mem.add_chunks(passages)
        self.persist_mem.save_sources(session_id, self.session_mem.retrieved_sources)

        for tc in retrieval_res["tool_call_log"]:
            self.session_mem.add_timeline_event(
                agent_name="Source Retriever",
                action=f"Tool call: {tc['tool']}",
                status="completed" if tc["success"] else "warning",
                details=f"Query: '{tc['query']}' | Found: {tc['items_found']} results",
                tool_name=tc["tool"],
                tool_result_summary=tc["message"]
            )

        # 6. Agent 3: Evidence Extraction (OpenAI)
        if on_progress:
            on_progress("Evidence Extractor", "OpenAI is extracting verifiable claims and quotes...")
        self.session_mem.add_timeline_event(
            agent_name="Evidence Extractor (OpenAI)",
            action="Extracting grounded claims and verbatim excerpts",
            status="running"
        )
        extracted_claims = self.extractor.extract_evidence(
            retrieved_passages=passages,
            research_question=research_question,
            demo_mode=demo_mode
        )
        self.session_mem.add_claims(extracted_claims)
        self.persist_mem.save_evidence_items(session_id, extracted_claims)

        self.session_mem.add_timeline_event(
            agent_name="Evidence Extractor (OpenAI)",
            action="Extracted grounded claims",
            status="completed",
            details=f"Extracted {len(extracted_claims)} verifiable claims directly tied to source page numbers."
        )

        # 7. Agent 4: Comparative Analysis & Contradiction Detection
        if on_progress:
            on_progress("Research Analyst", "Comparing cross-source claims and detecting contradictions...")
        self.session_mem.add_timeline_event(
            agent_name="Research Analyst",
            action="Comparing contradictory claims and consensus",
            status="running"
        )
        analysis_res = self.analyst.analyze_evidence_and_contradictions(
            claims=extracted_claims,
            research_question=research_question,
            demo_mode=demo_mode
        )
        for c in analysis_res.get("contradictions", []):
            self.session_mem.add_contradiction(c)
            self.persist_mem.save_contradiction(session_id, c)

        contradictions_found = len(analysis_res.get("contradictions", []))
        self.session_mem.add_timeline_event(
            agent_name="Research Analyst",
            action="Comparative analysis complete",
            status="completed",
            details=f"Identified {len(analysis_res.get('agreements', []))} agreements and {contradictions_found} contradictory metric claims."
        )

        # 8. Agent 5: Synthesis Writing (OpenAI)
        if on_progress:
            on_progress("Synthesis Writer", "OpenAI is drafting the 14-section source-based research briefing...")
        self.session_mem.add_timeline_event(
            agent_name="Synthesis Writer (OpenAI)",
            action="Synthesizing executive summary and briefing",
            status="running"
        )
        draft_report = self.writer.write_briefing(
            research_question=research_question,
            research_plan=plan,
            sources=self.session_mem.retrieved_sources,
            passages=passages,
            claims=extracted_claims,
            analysis=analysis_res,
            report_length=scope_config.get("report_length", "medium"),
            demo_mode=demo_mode
        )
        self.session_mem.draft_report = draft_report

        self.session_mem.add_timeline_event(
            agent_name="Synthesis Writer (OpenAI)",
            action="Draft report synthesized",
            status="completed",
            details="Produced comprehensive 14-section report adhering to epistemic labeling standards."
        )

        # 9. Agent 6: Citation Quality Review (Anthropic Claude)
        if on_progress:
            on_progress("Citation Reviewer", "Anthropic Claude is auditing citation integrity and quotes...")
        self.session_mem.add_timeline_event(
            agent_name="Citation Reviewer (Claude)",
            action="Reviewing citations and quote authenticity",
            status="running",
            tool_name="CitationValidatorTool"
        )
        review_res = self.reviewer.review_report_citations(
            report_markdown=draft_report,
            retrieved_sources=self.session_mem.retrieved_sources,
            retrieved_passages=passages,
            demo_mode=demo_mode
        )
        self.session_mem.citation_score = review_res.get("citation_score", 1.0)
        self.session_mem.report_approved = review_res.get("approved", True)
        self.session_mem.final_report = draft_report

        self.session_mem.add_timeline_event(
            agent_name="Citation Reviewer (Claude)",
            action="Report ready",
            status="completed" if review_res.get("approved") else "warning",
            details=review_res.get("audit_summary", "Audit completed."),
            tool_name="CitationValidatorTool",
            tool_result_summary=f"Citation score: {self.session_mem.citation_score*100:.1f}%"
        )

        # 10. Persist Report in SQLite
        report_id = self.persist_mem.save_report(
            session_id=session_id,
            report_markdown=draft_report,
            report_json={
                "plan": plan,
                "analysis": analysis_res,
                "review": review_res
            },
            citation_score=self.session_mem.citation_score
        )

        if on_progress:
            on_progress("Complete", "Research briefing complete and citations certified.")

        return {
            "session_id": session_id,
            "report_id": report_id,
            "report_markdown": draft_report,
            "citation_score": self.session_mem.citation_score,
            "approved": self.session_mem.report_approved,
            "sources": self.session_mem.retrieved_sources,
            "passages": passages,
            "claims": extracted_claims,
            "contradictions": analysis_res.get("contradictions", []),
            "timeline": self.session_mem.timeline
        }
