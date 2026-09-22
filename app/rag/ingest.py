"""Turns extracted page text into overlapping chunks ready for embedding."""

import uuid

from app.config import settings


def chunk_text(
    pages: list[dict],
    paper_id: str,
    owner_id: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[dict]:
    """
    Split extracted pages into overlapping chunks.

    Splits on whitespace so a chunk never cuts a word in half (the previous
    implementation sliced raw character windows, which regularly split
    words and even mid-token, degrading embedding quality). Overlap is
    measured in words for the same reason.

    Each returned chunk is a fully self-describing dict:
      {chunk_id, paper_id, owner_id, page_number, text}
    which is exactly what VectorStore.add_chunks expects, and owner_id is
    what makes per-user retrieval scoping possible downstream.
    """
    chunk_size = chunk_size if chunk_size is not None else settings.chunk_size
    overlap = overlap if overlap is not None else settings.chunk_overlap

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    chunks: list[dict] = []

    for page in pages:
        words = page["text"].split()
        if not words:
            continue

        # Rough words-per-chunk budget derived from the character target,
        # so CHUNK_SIZE/CHUNK_OVERLAP (character counts) keep meaning
        # regardless of this word-based implementation.
        avg_word_len = max(1, len(page["text"]) // len(words))
        words_per_chunk = max(1, chunk_size // avg_word_len)
        words_overlap = max(0, min(words_per_chunk - 1, overlap // avg_word_len))
        step = max(1, words_per_chunk - words_overlap)

        start = 0
        chunk_index = 0
        while start < len(words):
            end = start + words_per_chunk
            piece = " ".join(words[start:end])
            chunks.append(
                {
                    "chunk_id": f"{paper_id}_p{page['page_number']}_c{chunk_index}_{uuid.uuid4().hex[:6]}",
                    "paper_id": paper_id,
                    "owner_id": owner_id,
                    "page_number": page["page_number"],
                    "text": piece,
                }
            )
            chunk_index += 1
            start += step

    return chunks
