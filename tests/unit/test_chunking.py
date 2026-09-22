import pytest

from app.rag.ingest import chunk_text


def _pages(*texts):
    return [{"page_number": i + 1, "text": t} for i, t in enumerate(texts)]


def test_chunk_text_never_splits_a_word():
    long_text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_text(_pages(long_text), paper_id="p1", owner_id="u1", chunk_size=100, overlap=20)

    assert len(chunks) > 1
    for c in chunks:
        for token in c["text"].split():
            assert token.startswith("word"), f"chunk contains a malformed token: {token!r}"


def test_chunk_text_includes_required_fields():
    chunks = chunk_text(
        _pages("hello world this is a test sentence"), paper_id="paper-abc", owner_id="owner-xyz"
    )
    assert chunks
    for c in chunks:
        assert c["paper_id"] == "paper-abc"
        assert c["owner_id"] == "owner-xyz"
        assert c["page_number"] == 1
        assert c["chunk_id"]
        assert c["text"]


def test_chunk_ids_are_unique():
    text = " ".join(f"w{i}" for i in range(300))
    chunks = chunk_text(_pages(text, text), paper_id="p1", owner_id="u1", chunk_size=50, overlap=10)
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))


def test_chunk_text_handles_empty_page():
    chunks = chunk_text(_pages("", "actual content here"), paper_id="p1", owner_id="u1")
    assert all(c["text"] for c in chunks)
    assert any(c["page_number"] == 2 for c in chunks)


def test_chunk_text_rejects_bad_overlap():
    with pytest.raises(ValueError):
        chunk_text(_pages("some text"), paper_id="p1", owner_id="u1", chunk_size=10, overlap=10)


def test_chunk_text_rejects_zero_chunk_size():
    with pytest.raises(ValueError):
        chunk_text(_pages("some text"), paper_id="p1", owner_id="u1", chunk_size=0)


def test_chunk_text_multiple_pages_preserve_page_numbers():
    chunks = chunk_text(
        _pages("first page text", "second page text", "third page text"), paper_id="p1", owner_id="u1"
    )
    pages_seen = {c["page_number"] for c in chunks}
    assert pages_seen == {1, 2, 3}
