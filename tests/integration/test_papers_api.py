import io


def _upload(client, headers, pdf_bytes, filename="paper.pdf"):
    return client.post(
        "/papers/upload",
        headers=headers,
        files={"file": (filename, io.BytesIO(pdf_bytes), "application/pdf")},
    )


def test_upload_requires_authentication(client, sample_pdf_bytes):
    resp = _upload(client, {}, sample_pdf_bytes)
    assert resp.status_code == 401


def test_upload_valid_pdf_succeeds(client, make_user, sample_pdf_bytes):
    _, _, headers = make_user()
    resp = _upload(client, headers, sample_pdf_bytes)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["paper_id"]
    assert body["filename"] == "paper.pdf"
    assert body["num_pages"] == 2
    assert body["num_chunks"] > 0


def test_upload_rejects_non_pdf_extension(client, make_user):
    _, _, headers = make_user()
    resp = client.post(
        "/papers/upload",
        headers=headers,
        files={"file": ("notes.txt", io.BytesIO(b"just some text"), "text/plain")},
    )
    assert resp.status_code == 400


def test_upload_rejects_empty_file(client, make_user):
    _, _, headers = make_user()
    resp = client.post(
        "/papers/upload",
        headers=headers,
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
    )
    assert resp.status_code == 400


def test_upload_rejects_corrupt_pdf_and_does_not_orphan_file(client, make_user):
    _, _, headers = make_user()
    resp = client.post(
        "/papers/upload",
        headers=headers,
        files={"file": ("fake.pdf", io.BytesIO(b"not a real pdf"), "application/pdf")},
    )
    assert resp.status_code == 400

    # Regression check: a failed ingest must not leave an orphaned file on disk.
    from app.config import settings

    leftover = list(settings.papers_dir.glob("*.pdf"))
    assert len(leftover) == 0


def test_list_papers_only_returns_own_papers(client, make_user, sample_pdf_bytes):
    _, _, headers_a = make_user()
    _, _, headers_b = make_user()

    _upload(client, headers_a, sample_pdf_bytes)

    resp_a = client.get("/papers/list", headers=headers_a)
    resp_b = client.get("/papers/list", headers=headers_b)

    assert resp_a.json()["count"] == 1
    assert resp_b.json()["count"] == 0


def test_delete_paper_removes_it(client, make_user, sample_pdf_bytes):
    _, _, headers = make_user()
    paper_id = _upload(client, headers, sample_pdf_bytes).json()["paper_id"]

    del_resp = client.delete(f"/papers/{paper_id}", headers=headers)
    assert del_resp.status_code == 204

    list_resp = client.get("/papers/list", headers=headers)
    assert list_resp.json()["count"] == 0


def test_delete_paper_cannot_target_another_users_paper(client, make_user, sample_pdf_bytes):
    _, _, headers_a = make_user()
    _, _, headers_b = make_user()

    paper_id = _upload(client, headers_a, sample_pdf_bytes).json()["paper_id"]

    resp = client.delete(f"/papers/{paper_id}", headers=headers_b)
    assert resp.status_code == 404

    list_resp = client.get("/papers/list", headers=headers_a)
    assert list_resp.json()["count"] == 1
