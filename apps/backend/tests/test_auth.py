"""Auth flow: signup, duplicate signup, login (good/bad), logout."""


async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "Welcome" in resp.json()["message"]


async def test_signup_and_login(client):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "user1@example.com", "password": "pass1234"},
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "User created successfully"

    # Duplicate signup is rejected
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "user1@example.com", "password": "pass1234"},
    )
    assert resp.status_code == 400

    # Correct password logs in and sets the auth cookie
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "user1@example.com", "password": "pass1234"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.cookies

    # Wrong password is rejected
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "user1@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


async def test_protected_route_requires_auth(client):
    resp = await client.get("/api/v1/workspaces/")
    assert resp.status_code == 401


async def test_logout(auth_client):
    resp = await auth_client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
