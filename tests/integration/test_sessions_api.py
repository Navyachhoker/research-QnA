def test_create_session(client, make_user):
    _, _, headers = make_user()
    resp = client.post("/sessions/", json={"name": "Research chat"}, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Research chat"
    assert body["id"]


def test_create_session_rejects_empty_name(client, make_user):
    _, _, headers = make_user()
    resp = client.post("/sessions/", json={"name": ""}, headers=headers)
    assert resp.status_code == 422


def test_list_sessions_only_shows_own_sessions(client, make_user):
    _, _, headers_a = make_user()
    _, _, headers_b = make_user()

    client.post("/sessions/", json={"name": "A's session"}, headers=headers_a)

    resp_a = client.get("/sessions/", headers=headers_a)
    resp_b = client.get("/sessions/", headers=headers_b)

    assert len(resp_a.json()) == 1
    assert len(resp_b.json()) == 0


def test_get_history_for_nonexistent_session_returns_404(client, make_user):
    _, _, headers = make_user()
    resp = client.get("/sessions/does-not-exist/history", headers=headers)
    assert resp.status_code == 404


def test_get_history_for_another_users_session_returns_404(client, make_user):
    _, _, headers_a = make_user()
    _, _, headers_b = make_user()

    session_id = client.post("/sessions/", json={"name": "Private"}, headers=headers_a).json()["id"]

    resp = client.get(f"/sessions/{session_id}/history", headers=headers_b)
    assert resp.status_code == 404


def test_delete_session(client, make_user):
    _, _, headers = make_user()
    session_id = client.post("/sessions/", json={"name": "Temp"}, headers=headers).json()["id"]

    del_resp = client.delete(f"/sessions/{session_id}", headers=headers)
    assert del_resp.status_code == 204

    list_resp = client.get("/sessions/", headers=headers)
    assert len(list_resp.json()) == 0


def test_delete_another_users_session_returns_404(client, make_user):
    _, _, headers_a = make_user()
    _, _, headers_b = make_user()

    session_id = client.post("/sessions/", json={"name": "Private"}, headers=headers_a).json()["id"]

    resp = client.delete(f"/sessions/{session_id}", headers=headers_b)
    assert resp.status_code == 404
