def test_register_creates_user_and_returns_token(client):
    resp = client.post("/auth/register", json={"email": "new@example.com", "password": "password123"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "new@example.com"
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_register_duplicate_email_returns_409(client):
    client.post("/auth/register", json={"email": "dupe@example.com", "password": "password123"})
    resp = client.post("/auth/register", json={"email": "dupe@example.com", "password": "different-pass"})
    assert resp.status_code == 409


def test_register_rejects_short_password(client):
    resp = client.post("/auth/register", json={"email": "short@example.com", "password": "abc"})
    assert resp.status_code == 422


def test_register_rejects_invalid_email(client):
    resp = client.post("/auth/register", json={"email": "not-an-email", "password": "password123"})
    assert resp.status_code == 422


def test_login_succeeds_with_correct_credentials(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "password123"})
    resp = client.post("/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_fails_with_wrong_password(client):
    client.post("/auth/register", json={"email": "login2@example.com", "password": "password123"})
    resp = client.post("/auth/login", json={"email": "login2@example.com", "password": "wrong-password"})
    assert resp.status_code == 401


def test_login_fails_for_unknown_user(client):
    resp = client.post("/auth/login", json={"email": "nobody@example.com", "password": "whatever123"})
    assert resp.status_code == 401


def test_me_requires_authentication(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, make_user):
    email, _password, headers = make_user()
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == email


def test_me_rejects_garbage_token(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401
