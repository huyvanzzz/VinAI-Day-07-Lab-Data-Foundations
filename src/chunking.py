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


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        stripped = text.strip()
        if not stripped:
            return []

        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", stripped) if sentence.strip()]
        if not sentences:
            return [stripped]

        chunks: list[str] = []
        for start in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[start : start + self.max_sentences_per_chunk]
            chunks.append(" ".join(group).strip())
        return chunks


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
        stripped = text.strip()
        if not stripped:
            return []

        separators = self.separators or [""]
        return [chunk.strip() for chunk in self._split(stripped, separators) if chunk.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        stripped = current_text.strip()
        if not stripped:
            return []
        if len(stripped) <= self.chunk_size:
            return [stripped]

        if not remaining_separators:
            return FixedSizeChunker(chunk_size=self.chunk_size, overlap=0).chunk(stripped)

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        if separator == "":
            return FixedSizeChunker(chunk_size=self.chunk_size, overlap=0).chunk(stripped)

        pieces = stripped.split(separator)
        if len(pieces) == 1:
            return self._split(stripped, next_separators)

        chunks: list[str] = []
        buffer = ""

        for index, piece in enumerate(pieces):
            if not piece and index == len(pieces) - 1:
                continue

            unit = piece if index == len(pieces) - 1 else piece + separator

            if len(unit) > self.chunk_size:
                if buffer.strip():
                    chunks.append(buffer.strip())
                    buffer = ""
                chunks.extend(self._split(unit, next_separators))
                continue

            if not buffer:
                buffer = unit
            elif len(buffer) + len(unit) <= self.chunk_size:
                buffer += unit
            else:
                chunks.append(buffer.strip())
                buffer = unit

        if buffer.strip():
            chunks.append(buffer.strip())

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    magnitude_a = math.sqrt(sum(value * value for value in vec_a))
    magnitude_b = math.sqrt(sum(value * value for value in vec_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return _dot(vec_a, vec_b) / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        normalized_chunk_size = max(1, chunk_size)
        fixed_overlap = min(50, max(0, normalized_chunk_size // 5))
        sentence_limit = max(1, normalized_chunk_size // 100)

        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=normalized_chunk_size, overlap=fixed_overlap),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=sentence_limit),
            "recursive": RecursiveChunker(chunk_size=normalized_chunk_size),
        }

        comparison: dict[str, dict] = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            avg_length = sum(len(chunk) for chunk in chunks) / len(chunks) if chunks else 0.0
            comparison[name] = {
                "count": len(chunks),
                "avg_length": avg_length,
                "chunks": chunks,
            }

        return comparison
