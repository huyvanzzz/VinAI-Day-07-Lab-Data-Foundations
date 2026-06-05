from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks

    def split_documents(self, docs: list[Document]) -> list[Document]:
        """Split a list of documents into chunks while preserving metadata."""
        chunked_docs = []
        for doc in docs:
            chunks = self.chunk(doc.content)
            for i, chunk_text in enumerate(chunks):
                # Copy original metadata and add traceability info
                metadata = doc.metadata.copy()
                metadata["source_id"] = doc.id
                metadata["chunk_index"] = i
                chunked_docs.append(Document(
                    id=f"{doc.id}_chunk_{i}",
                    content=chunk_text,
                    metadata=metadata
                ))
        return chunked_docs


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        # Split into sentences using regex
        # We look for . ! ? followed by space or newline, or end of string
        sentences = re.split(r'(?<=[.!?])(?:\s+|\n)', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk_sentences = sentences[i : i + self.max_sentences_per_chunk]
            chunks.append(" ".join(chunk_sentences))
        
        return chunks

    def split_documents(self, docs: list[Document]) -> list[Document]:
        """Split a list of documents into chunks while preserving metadata."""
        chunked_docs = []
        for doc in docs:
            chunks = self.chunk(doc.content)
            for i, chunk_text in enumerate(chunks):
                metadata = doc.metadata.copy()
                metadata["source_id"] = doc.id
                metadata["chunk_index"] = i
                chunked_docs.append(Document(
                    id=f"{doc.id}_chunk_{i}",
                    content=chunk_text,
                    metadata=metadata
                ))
        return chunked_docs


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]
        
        if not remaining_separators:
            # If no more separators, just split by chunk_size
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        separator = remaining_separators[0]
        new_separators = remaining_separators[1:]
        
        if separator == "":
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        # Try to split by current separator
        parts = current_text.split(separator)
        
        final_chunks = []
        current_buffer = ""
        
        for i, part in enumerate(parts):
            # Add separator back if it's not the last part
            piece = part + (separator if i < len(parts) - 1 else "")
            
            if len(piece) > self.chunk_size:
                # If buffer has content, flush it first
                if current_buffer:
                    final_chunks.append(current_buffer)
                    current_buffer = ""
                
                # Recursively split the oversized piece
                final_chunks.extend(self._split(piece, new_separators))
            else:
                if len(current_buffer) + len(piece) <= self.chunk_size:
                    current_buffer += piece
                else:
                    if current_buffer:
                        final_chunks.append(current_buffer)
                    current_buffer = piece
        
        if current_buffer:
            final_chunks.append(current_buffer)
            
        return [c for c in final_chunks if c]

    def split_documents(self, docs: list[Document]) -> list[Document]:
        """Split a list of documents into chunks while preserving metadata."""
        chunked_docs = []
        for doc in docs:
            chunks = self.chunk(doc.content)
            for i, chunk_text in enumerate(chunks):
                metadata = doc.metadata.copy()
                metadata["source_id"] = doc.id
                metadata["chunk_index"] = i
                chunked_docs.append(Document(
                    id=f"{doc.id}_chunk_{i}",
                    content=chunk_text,
                    metadata=metadata
                ))
        return chunked_docs


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_prod = _dot(vec_a, vec_b)
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(x * x for x in vec_b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_prod / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size)
        }
        
        results = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            if not chunks:
                results[name] = {"count": 0, "avg_length": 0.0, "chunks": []}
            else:
                avg_len = sum(len(c) for c in chunks) / len(chunks)
                results[name] = {
                    "count": len(chunks),
                    "avg_length": avg_len,
                    "chunks": chunks
                }
        
        return results
