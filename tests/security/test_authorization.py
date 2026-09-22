"""
These tests exist because of a real finding from the audit: the original
VectorStore had NO per-user scoping at all. Any authenticated user's
question could retrieve — and get answered using — chunks from any other
user's uploaded papers. `search()` even used a single global collection
with no owner filter whatsoever, so leaving `paper` unset in a query meant
searching every user's documents at once.

These tests assert that can never regress.
"""

import io


def _upload(client, headers, pdf_bytes, filename="paper.pdf"):
    return client.post(
        "/papers/upload",
        headers=headers,
        files={"file": (filename, io.BytesIO(pdf_bytes), "application/pdf")},
    )


def test_vector_store_search_never_crosses_owner_boundary(real_vector_store):
    real_vector_store.add_chunks(
        [
            {
                "chunk_id": "c1",
                "paper_id": "paper-1",
                "owner_id": "user-a",
                "page_number": 1,
                "text": "Alpha secret research findings.",
            },
            {
                "chunk_id": "c2",
                "paper_id": "paper-2",
                "owner_id": "user-b",
                "page_number": 1,
                "text": "Beta secret research findings.",
            },
        ]
    )

    results_for_a = real_vector_store.search("secret research findings", owner_id="user-a", top_k=10)
    results_for_b = real_vector_store.search("secret research findings", owner_id="user-b", top_k=10)

    assert {r["chunk_id"] for r in results_for_a} == {"c1"}
    assert {r["chunk_id"] for r in results_for_b} == {"c2"}


def test_vector_store_search_with_no_paper_filter_still_respects_owner(real_vector_store):
    """The most severe version of the original bug: an unscoped query
    (paper=None) must still never return another user's chunks."""
    real_vector_store.add_chunks(
        [
            {
                "chunk_id": f"c{i}",
                "paper_id": "shared-looking-id",
                "owner_id": "user-a",
                "page_number": 1,
                "text": f"user a chunk {i}",
            }
            for i in range(5)
        ]
    )
    real_vector_store.add_chunks(
        [
            {
                "chunk_id": f"d{i}",
                "paper_id": "shared-looking-id",
                "owner_id": "user-b",
                "page_number": 1,
                "text": f"user b chunk {i}",
            }
            for i in range(5)
        ]
    )

    results = real_vector_store.search("chunk", owner_id="user-a", top_k=20)
    assert all(r["chunk_id"].startswith("c") for r in results)
    assert len(results) == 5


def test_vector_store_get_all_chunks_scoped_by_owner(real_vector_store):
    real_vector_store.add_chunks(
        [
            {"chunk_id": "c1", "paper_id": "shared-id", "owner_id": "user-a", "page_number": 1, "text": "a"},
            {"chunk_id": "c2", "paper_id": "shared-id", "owner_id": "user-b", "page_number": 1, "text": "b"},
        ]
    )

    chunks_a = real_vector_store.get_all_chunks_for_paper("shared-id", owner_id="user-a")
    assert [c["chunk_id"] for c in chunks_a] == ["c1"]


def test_vector_store_delete_scoped_by_owner_does_not_touch_other_owners_chunks(real_vector_store):
    real_vector_store.add_chunks(
        [
            {"chunk_id": "c1", "paper_id": "shared-id", "owner_id": "user-a", "page_number": 1, "text": "a"},
            {"chunk_id": "c2", "paper_id": "shared-id", "owner_id": "user-b", "page_number": 1, "text": "b"},
        ]
    )

    real_vector_store.delete_paper_chunks("shared-id", owner_id="user-a")

    remaining_b = real_vector_store.get_all_chunks_for_paper("shared-id", owner_id="user-b")
    assert len(remaining_b) == 1


def test_end_to_end_qa_never_leaks_another_users_paper(client, make_user, sample_pdf_bytes):
    """Full-stack version of the same check, through the real API."""
    _, _, headers_a = make_user()
    _, _, headers_b = make_user()

    _upload(client, headers_a, sample_pdf_bytes)  # user A has a paper, user B has none

    resp_b = client.post("/qa/ask", json={"question": "What does the paper discuss?"}, headers=headers_b)
    assert resp_b.status_code == 200
    assert resp_b.json()["sources"] == []  # nothing for B — A's paper must not leak in


def test_end_to_end_session_history_isolated_per_user(client, make_user):
    _, _, headers_a = make_user()
    _, _, headers_b = make_user()

    client.post("/sessions/", json={"name": "A's private session"}, headers=headers_a)

    sessions_b = client.get("/sessions/", headers=headers_b).json()
    assert sessions_b == []
