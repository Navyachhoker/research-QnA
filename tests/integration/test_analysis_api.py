import io


def _upload(client, headers, pdf_bytes, filename="paper.pdf"):
    return client.post(
        "/papers/upload",
        headers=headers,
        files={"file": (filename, io.BytesIO(pdf_bytes), "application/pdf")},
    )


def test_summarize_requires_authentication(client):
    resp = client.post("/analysis/summarize", json={"paper_id": "whatever"})
    assert resp.status_code == 401


def test_summarize_unknown_paper_returns_404(client, make_user):
    _, _, headers = make_user()
    resp = client.post("/analysis/summarize", json={"paper_id": "nope"}, headers=headers)
    assert resp.status_code == 404


def test_summarize_own_paper_succeeds(client, make_user, sample_pdf_bytes):
    _, _, headers = make_user()
    paper_id = _upload(client, headers, sample_pdf_bytes).json()["paper_id"]

    resp = client.post("/analysis/summarize", json={"paper_id": paper_id}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["summary"]


def test_summarize_cannot_target_another_users_paper(client, make_user, sample_pdf_bytes):
    _, _, headers_a = make_user()
    _, _, headers_b = make_user()
    paper_id = _upload(client, headers_a, sample_pdf_bytes).json()["paper_id"]

    resp = client.post("/analysis/summarize", json={"paper_id": paper_id}, headers=headers_b)
    assert resp.status_code == 404


def test_compare_two_own_papers(client, make_user, sample_pdf_bytes):
    _, _, headers = make_user()
    paper_a = _upload(client, headers, sample_pdf_bytes, "a.pdf").json()["paper_id"]
    paper_b = _upload(client, headers, sample_pdf_bytes, "b.pdf").json()["paper_id"]

    resp = client.post(
        "/analysis/compare", json={"paper_a_id": paper_a, "paper_b_id": paper_b}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["comparison"]


def test_compare_rejects_paper_owned_by_someone_else(client, make_user, sample_pdf_bytes):
    _, _, headers_a = make_user()
    _, _, headers_b = make_user()
    paper_a = _upload(client, headers_a, sample_pdf_bytes, "a.pdf").json()["paper_id"]
    paper_b = _upload(client, headers_b, sample_pdf_bytes, "b.pdf").json()["paper_id"]

    resp = client.post(
        "/analysis/compare", json={"paper_a_id": paper_a, "paper_b_id": paper_b}, headers=headers_a
    )
    assert resp.status_code == 404


def test_related_work_by_topic(client, make_user, sample_pdf_bytes):
    _, _, headers = make_user()
    _upload(client, headers, sample_pdf_bytes)

    resp = client.post("/analysis/related-work", json={"topic": "attention mechanisms"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["topic"] == "attention mechanisms"


def test_related_work_rejects_too_short_topic(client, make_user):
    _, _, headers = make_user()
    resp = client.post("/analysis/related-work", json={"topic": "a"}, headers=headers)
    assert resp.status_code == 422
