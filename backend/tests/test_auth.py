def test_register_and_login(client):
    r = client.post("/auth/register", json={"email": "a@example.com", "password": "SuperSecret123"})
    assert r.status_code == 201

    r = client.post("/auth/login", json={"email": "a@example.com", "password": "SuperSecret123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_duplicate_register_fails(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "SuperSecret123"})
    r = client.post("/auth/register", json={"email": "dup@example.com", "password": "SuperSecret123"})
    assert r.status_code == 400


def test_wrong_password_fails(client):
    client.post("/auth/register", json={"email": "b@example.com", "password": "SuperSecret123"})
    r = client.post("/auth/login", json={"email": "b@example.com", "password": "WrongPassword"})
    assert r.status_code == 401


def test_me_requires_token(client):
    r = client.get("/auth/me")
    assert r.status_code in (401, 403)


def test_me_returns_correct_user(client, make_user):
    user = make_user(email="c@example.com")
    r = client.get("/auth/me", headers=user["headers"])
    assert r.status_code == 200
    assert r.json()["email"] == "c@example.com"


def test_invalid_token_rejected(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401