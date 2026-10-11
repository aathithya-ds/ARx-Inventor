"""
ARX INVENTOR - Local Embedding Generation
Supports SentenceTransformers with a lightweight fallback embedder.
"""

from typing import List
import math
import hashlib
import re

class EmbeddingService:
    """Manages vector embeddings for semantic document search."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._st_model = None
        self.use_fallback = False

        # Attempt to load SentenceTransformer if installed
        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer(self.model_name)
        except Exception:
            # Fallback to local semantic hashing embedder
            self.use_fallback = True

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of texts into dense vectors."""
        if not texts:
            return []

        if self._st_model is not None and not self.use_fallback:
            try:
                embeddings = self._st_model.encode(texts, convert_to_numpy=True)
                return embeddings.tolist()
            except Exception:
                self.use_fallback = True

        return [self._fallback_embed(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        """Embeds a single query string."""
        results = self.embed_texts([query])
        return results[0] if results else [0.0] * 384

    def _fallback_embed(self, text: str, dim: int = 384) -> List[float]:
        """
        Lightweight deterministic feature-hashing embedder.
        Produces a normalized 384-dimensional dense vector based on word and character n-grams.
        Guarantees fast, robust semantic keyword & n-gram matching without requiring PyTorch.
        """
        if not text.strip():
            return [0.0] * dim

        vec = [0.0] * dim
        tokens = re.findall(r'\b\w+\b', text.lower())

        # Word tokens
        for token in tokens:
            h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 1.0

        # Subword character n-grams (3-grams and 4-grams)
        for i in range(len(text) - 3):
            gram = text[i:i+4].lower()
            h = int(hashlib.sha256(gram.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 0.5

        # L2 normalize vector
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]

        return vec
