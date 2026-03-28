"""Text chunking utilities for corpus ingestion."""

import re


def chunk_text(
    text: str, chunk_size: int = 500, overlap: int = 50
) -> list[str]:
    """Split text into chunks by character count with overlap.

    Prefers splitting at paragraph or sentence boundaries when possible.

    Parameters
    ----------
    text:
        The text to split into chunks.
    chunk_size:
        Target size for each chunk in characters.
    overlap:
        Number of overlapping characters between consecutive chunks.

    Returns
    -------
    list[str]
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Try to find a paragraph boundary (double newline) near the end
        candidate = text[start:end]
        para_break = candidate.rfind("\n\n")
        if para_break > chunk_size // 3:
            end = start + para_break + 2  # include the double newline
        else:
            # Try to find a sentence boundary (. ! ?)
            sentence_match = None
            for m in re.finditer(r"[.!?]\s", candidate):
                if m.end() > chunk_size // 3:
                    sentence_match = m
            if sentence_match is not None:
                end = start + sentence_match.end()
            # else: hard split at chunk_size (already set)

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start forward, accounting for overlap
        start = max(start + 1, end - overlap)

    return chunks
