"""
ARX INVENTOR - Agent 2: Source Retriever
Role: Source Retrieval Specialist
Objective: Executes tool calls to search uploaded documents and permitted web sources,
recording source IDs, page numbers, URLs, and retrieval timestamps.
"""

from typing import List, Dict, Any, Optional
import datetime
from tools.rag_retriever import RAGRetrieverTool
from tools.approved_web_search import ApprovedWebSearchTool

class SourceRetrieverAgent:
    """Agent 2: Executes retrieval tools against document and web corpora."""

    def __init__(
        self,
        rag_tool: RAGRetrieverTool,
        web_search_tool: Optional[ApprovedWebSearchTool] = None
    ):
        self.rag_tool = rag_tool
        self.web_search_tool = web_search_tool
        self.role = "Source Retrieval Specialist"
        self.goal = "Retrieve verifiable evidence passages from approved documents and safe web sources."
        self.backstory = (
            "You are a dedicated retrieval specialist. You only present genuine excerpts with "
            "verifiable source identifiers, page numbers, and exact text."
        )

    def retrieve_for_subquestions(
        self,
        subquestions: List[str],
        session_id: Optional[str] = None,
        enable_web_search: bool = False,
        source_priority: str = "documents_first",
        top_k: int = 4
    ) -> Dict[str, Any]:
        """
        Executes real tool queries for each subquestion.
        Returns:
        {
            "passages": list[dict],
            "sources": list[dict], # List of registered sources [S1], [S2]...
            "tool_call_log": list[dict]
        }
        """
        all_passages = []
        source_registry: Dict[str, Dict[str, Any]] = {}
        tool_call_log = []
        source_counter = 1

        for sq in subquestions:
            # 1. RAG Retrieval from uploaded documents
            tool_start = datetime.datetime.now().isoformat()
            rag_res = self.rag_tool.retrieve_evidence(
                query=sq,
                top_k=top_k,
                session_id=session_id
            )

            tool_call_log.append({
                "tool": "RAGRetrieverTool",
                "query": sq,
                "timestamp": tool_start,
                "success": rag_res.get("success", False),
                "items_found": rag_res.get("total_retrieved", 0),
                "message": rag_res.get("message", "")
            })

            if rag_res.get("success") and rag_res.get("passages"):
                for p in rag_res["passages"]:
                    doc_name = p.get("document_name", "Uploaded Document")
                    if doc_name not in source_registry:
                        s_label = f"S{source_counter}"
                        source_counter += 1
                        source_registry[doc_name] = {
                            "source_id_label": s_label,
                            "source_type": "document",
                            "title": doc_name,
                            "identifier": doc_name,
                            "page_or_section": f"Page {p.get('page_number', 1)}",
                            "retrieval_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    # Map source label to passage
                    p_copy = dict(p)
                    p_copy["source_id"] = source_registry[doc_name]["source_id_label"]
                    all_passages.append(p_copy)

            # 2. Web Retrieval (if enabled and requested)
            if enable_web_search and self.web_search_tool:
                web_start = datetime.datetime.now().isoformat()
                web_res = self.web_search_tool.search(sq)
                tool_call_log.append({
                    "tool": "ApprovedWebSearchTool",
                    "query": sq,
                    "timestamp": web_start,
                    "success": web_res.get("success", False),
                    "items_found": web_res.get("total_found", 0),
                    "message": web_res.get("error") or "Web search completed"
                })

                if web_res.get("success") and web_res.get("results"):
                    for item in web_res["results"][:2]: # fetch top 2 search results
                        url = item.get("url", "")
                        if not url:
                            continue
                        # Fetch safe page content
                        fetch_res = self.web_search_tool.fetch_webpage_content(url)
                        if fetch_res.get("success") and fetch_res.get("text"):
                            if url not in source_registry:
                                s_label = f"S{source_counter}"
                                source_counter += 1
                                source_registry[url] = {
                                    "source_id_label": s_label,
                                    "source_type": "web_page",
                                    "title": fetch_res.get("title", item.get("title", "Web Source")),
                                    "identifier": url,
                                    "page_or_section": "Web Document",
                                    "retrieval_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                            # Add top excerpt as a passage
                            clean_excerpt = fetch_res["text"][:600]
                            all_passages.append({
                                "source_id": source_registry[url]["source_id_label"],
                                "document_name": source_registry[url]["title"],
                                "page_number": 1,
                                "chunk_id": f"web_{len(all_passages)}",
                                "score": 0.85,
                                "text": clean_excerpt
                            })

        # Deduplicate passages by text content
        unique_passages = []
        seen_texts = set()
        for p in all_passages:
            t_snippet = p["text"][:100].strip()
            if t_snippet not in seen_texts:
                seen_texts.add(t_snippet)
                unique_passages.append(p)

        return {
            "passages": unique_passages,
            "sources": list(source_registry.values()),
            "tool_call_log": tool_call_log
        }
