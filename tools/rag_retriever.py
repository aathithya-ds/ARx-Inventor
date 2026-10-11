"""
ARX INVENTOR - Tool B: RAG Retriever
Ingests parsed documents, generates embeddings, stores them in vector storage,
and semantically retrieves evidence passages with similarity scores and page numbers.
"""

from typing import List, Dict, Any, Optional
from rag.chunking import TextChunker
from rag.vector_store import VectorStore
from config.settings import settings

class RAGRetrieverTool:
    """RAG tool for document ingestion and semantic evidence retrieval."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or VectorStore()
        self.chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def ingest_document(
        self,
        document_name: str,
        pages: List[Dict[str, Any]],
        source_id: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chunks pages and indexes them in vector storage.
        """
        if not pages:
            return {
                "success": False,
                "chunks_created": 0,
                "message": f"No extractable pages found for {document_name}"
            }

        chunks = self.chunker.chunk_document_pages(
            pages=pages,
            document_name=document_name,
            source_id=source_id
        )

        if not chunks:
            return {
                "success": False,
                "chunks_created": 0,
                "message": f"Chunking resulted in 0 chunks for {document_name}"
            }

        self.vector_store.add_chunks(chunks, session_id=session_id)
        return {
            "success": True,
            "source_id": source_id,
            "document_name": document_name,
            "chunks_created": len(chunks),
            "sample_chunk_id": chunks[0]["chunk_id"] if chunks else None
        }

    def retrieve_evidence(
        self,
        query: str,
        top_k: int = settings.TOP_K_CHUNKS,
        min_score: float = settings.MIN_SIMILARITY_SCORE,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves top relevant passages.
        Returns:
        {
            "success": bool,
            "query": str,
            "total_retrieved": int,
            "passages": [
                {
                    "source_id": str,
                    "document_name": str,
                    "page_number": int,
                    "chunk_id": str,
                    "score": float,
                    "text": str
                }
            ],
            "message": str
        }
        """
        if not query.strip():
            return {
                "success": False,
                "query": query,
                "total_retrieved": 0,
                "passages": [],
                "message": "Empty query provided for retrieval."
            }

        results = self.vector_store.search(
            query=query,
            top_k=top_k,
            min_score=min_score,
            session_id=session_id
        )

        if not results:
            return {
                "success": False,
                "query": query,
                "total_retrieved": 0,
                "passages": [],
                "message": f"No relevant evidence found above similarity threshold ({min_score}) for query."
            }

        return {
            "success": True,
            "query": query,
            "total_retrieved": len(results),
            "passages": results,
            "message": f"Retrieved {len(results)} relevant passages."
        }
