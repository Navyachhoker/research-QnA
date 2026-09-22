import io


def _upload(client, headers, pdf_bytes, filename="paper.pdf"):
    return client.post(
        "/papers/upload",
        headers=headers,
        files={"file": (filename, io.BytesIO(pdf_bytes), "application/pdf")},
    )


def test_ask_requires_authentication(client):
    resp = client.post("/qa/ask", json={"question": "What is attention?"})
    assert resp.status_code == 401


def test_ask_with_no_papers_returns_empty_answer(client, make_user):
    _, _, headers = make_user()
    resp = client.post("/qa/ask", json={"question": "What is attention?"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["sources"] == []


def test_ask_returns_answer_with_sources_after_upload(client, make_user, sample_pdf_bytes):
    _, _, headers = make_user()
    _upload(client, headers, sample_pdf_bytes)

    resp = client.post("/qa/ask", json={"question": "What does the paper discuss?"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"]
    assert len(body["sources"]) > 0
    assert body["sources"][0]["source_num"] == 1


def test_ask_with_unknown_paper_id_returns_404(client, make_user):
    _, _, headers = make_user()
    resp = client.post(
        "/qa/ask", json={"question": "test?", "paper": "nonexistent-paper-id"}, headers=headers
    )
    assert resp.status_code == 404


def test_ask_scoped_to_a_specific_paper_the_user_owns(client, make_user, sample_pdf_bytes):
    _, _, headers = make_user()
    paper_id = _upload(client, headers, sample_pdf_bytes).json()["paper_id"]

    resp = client.post("/qa/ask", json={"question": "test?", "paper": paper_id}, headers=headers)
    assert resp.status_code == 200


def test_ask_with_session_id_persists_history(client, make_user, sample_pdf_bytes):
    _, _, headers = make_user()
    _upload(client, headers, sample_pdf_bytes)

    session_resp = client.post("/sessions/", json={"name": "My session"}, headers=headers)
    session_id = session_resp.json()["id"]

    client.post("/qa/ask", json={"question": "first question", "session_id": session_id}, headers=headers)
    client.post("/qa/ask", json={"question": "second question", "session_id": session_id}, headers=headers)

    history_resp = client.get(f"/sessions/{session_id}/history", headers=headers)
    turns = history_resp.json()["turns"]
    assert len(turns) == 2
    assert turns[0]["question"] == "first question"
    assert turns[1]["question"] == "second question"


def test_ask_rejects_unknown_session_id(client, make_user):
    _, _, headers = make_user()
    resp = client.post(
        "/qa/ask", json={"question": "test?", "session_id": "nonexistent-session"}, headers=headers
    )
    assert resp.status_code == 404


def test_ask_rejects_empty_question(client, make_user):
    _, _, headers = make_user()
    resp = client.post("/qa/ask", json={"question": ""}, headers=headers)
    assert resp.status_code == 422
