"""
ARX INVENTOR - Vector Store
Manages ChromaDB persistent vector storage with cosine similarity retrieval.
"""

from typing import List, Dict, Any, Optional
import math
from pathlib import Path
from config.settings import settings
from rag.embeddings import EmbeddingService

class VectorStore:
    """Manages document vector embeddings and semantic search."""

    def __init__(self, persist_dir: Optional[Path] = None, collection_name: str = "arx_research"):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService(settings.EMBEDDING_MODEL_NAME)
        
        self._chroma_client = None
        self._collection = None
        self._fallback_records: List[Dict[str, Any]] = []

        self._init_store()

    def _init_store(self):
        """Initializes ChromaDB or falls back to in-memory vector index."""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            self._chroma_client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self._collection = self._chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            # Fallback to local memory vector collection
            self._chroma_client = None
            self._collection = None

    def add_chunks(self, chunks: List[Dict[str, Any]], session_id: Optional[str] = None):
        """Adds text chunks with embeddings and metadata to the store."""
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.embed_texts(texts)
        ids = [c["chunk_id"] for c in chunks]
        metadatas = []
        for c in chunks:
            meta = {
                "source_id": str(c.get("source_id", "S1")),
                "document_name": str(c.get("document_name", "")),
                "page_number": int(c.get("page_number", 1)),
                "char_count": int(c.get("char_count", len(c.get("text", "")))),
                "session_id": str(session_id or "global")
            }
            metadatas.append(meta)

        if self._collection is not None:
            try:
                self._collection.upsert(
                    ids=ids,
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                return
            except Exception:
                pass

        # Fallback local index
        for i, chunk in enumerate(chunks):
            self._fallback_records.append({
                "chunk_id": ids[i],
                "text": texts[i],
                "embedding": embeddings[i],
                "metadata": metadatas[i]
            })

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.20,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant chunks with similarity score.
        Returns list of {source_id, document_name, page_number, chunk_id, score, text}.
        """
        if not query.strip():
            return []

        query_emb = self.embedding_service.embed_query(query)

        if self._collection is not None:
            try:
                where_clause = {"session_id": session_id} if session_id else None
                res = self._collection.query(
                    query_embeddings=[query_emb],
                    n_results=top_k,
                    where=where_clause
                )
                results = []
                if res and res["documents"] and res["documents"][0]:
                    docs = res["documents"][0]
                    ids = res["ids"][0]
                    metas = res["metadatas"][0]
                    distances = res["distances"][0] if "distances" in res and res["distances"] else [0.0] * len(docs)

                    for idx, doc in enumerate(docs):
                        dist = distances[idx]
                        # In Chroma cosine distance: similarity = 1 - distance
                        similarity = max(0.0, 1.0 - dist)
                        if similarity >= min_score:
                            results.append({
                                "chunk_id": ids[idx],
                                "source_id": metas[idx].get("source_id", "S1"),
                                "document_name": metas[idx].get("document_name", ""),
                                "page_number": metas[idx].get("page_number", 1),
                                "score": round(similarity, 4),
                                "text": doc
                            })
                return results
            except Exception:
                pass

        # Fallback search
        scored_items = []
        for rec in self._fallback_records:
            if session_id and rec["metadata"].get("session_id") != session_id:
                continue
            rec_emb = rec["embedding"]
            # Cosine similarity
            dot = sum(a * b for a, b in zip(query_emb, rec_emb))
            norm_q = math.sqrt(sum(a * a for a in query_emb))
            norm_r = math.sqrt(sum(b * b for b in rec_emb))
            sim = dot / (norm_q * norm_r) if norm_q > 0 and norm_r > 0 else 0.0

            if sim >= min_score:
                scored_items.append((
                    sim,
                    {
                        "chunk_id": rec["chunk_id"],
                        "source_id": rec["metadata"].get("source_id", "S1"),
                        "document_name": rec["metadata"].get("document_name", ""),
                        "page_number": rec["metadata"].get("page_number", 1),
                        "score": round(sim, 4),
                        "text": rec["text"]
                    }
                ))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_items[:top_k]]

    def clear(self, session_id: Optional[str] = None):
        """Clears vectors for a specific session or entire collection."""
        if self._collection is not None:
            try:
                if session_id:
                    self._collection.delete(where={"session_id": session_id})
                else:
                    self._chroma_client.delete_collection(self.collection_name)
                    self._collection = self._chroma_client.create_collection(
                        self.collection_name,
                        metadata={"hnsw:space": "cosine"}
                    )
            except Exception:
                pass

        if session_id:
            self._fallback_records = [
                r for r in self._fallback_records
                if r["metadata"].get("session_id") != session_id
            ]
        else:
            self._fallback_records.clear()
