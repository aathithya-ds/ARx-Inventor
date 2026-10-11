"""
ARX INVENTOR - Text Chunking Pipeline
Splits document text into overlapping chunks while preserving document names, page numbers, and boundaries.
"""

from typing import List, Dict, Any
import re
import uuid

class TextChunker:
    """Chunks text with sliding window and metadata tracking."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document_pages(
        self,
        pages: List[Dict[str, Any]],
        document_name: str,
        source_id: str = "S1"
    ) -> List[Dict[str, Any]]:
        """
        Chunks text from structured page records.
        pages: List of {"page_number": int, "text": str}
        Returns list of chunk dicts.
        """
        all_chunks = []
        global_chunk_idx = 0

        for page_data in pages:
            page_num = page_data.get("page_number", 1)
            raw_text = page_data.get("text", "").strip()
            if not raw_text:
                continue

            # Clean and normalize text while preserving paragraph breaks
            cleaned_text = re.sub(r'\r\n', '\n', raw_text)
            cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
            paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]

            # Build overlapping windows
            current_window = []
            current_length = 0

            for para in paragraphs:
                para_len = len(para)
                if current_length + para_len > self.chunk_size and current_window:
                    chunk_content = "\n\n".join(current_window)
                    chunk_id = f"{source_id}_p{page_num}_c{global_chunk_idx}"
                    all_chunks.append({
                        "chunk_id": chunk_id,
                        "source_id": source_id,
                        "document_name": document_name,
                        "page_number": page_num,
                        "text": chunk_content,
                        "char_count": len(chunk_content)
                    })
                    global_chunk_idx += 1

                    # Compute overlap from end of current window
                    overlap_chars = 0
                    new_window = []
                    for item in reversed(current_window):
                        if overlap_chars + len(item) <= self.chunk_overlap:
                            new_window.insert(0, item)
                            overlap_chars += len(item)
                        else:
                            break
                    current_window = new_window
                    current_length = sum(len(x) for x in current_window)

                current_window.append(para)
                current_length += para_len

            if current_window:
                chunk_content = "\n\n".join(current_window)
                chunk_id = f"{source_id}_p{page_num}_c{global_chunk_idx}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "source_id": source_id,
                    "document_name": document_name,
                    "page_number": page_num,
                    "text": chunk_content,
                    "char_count": len(chunk_content)
                })
                global_chunk_idx += 1

        return all_chunks
