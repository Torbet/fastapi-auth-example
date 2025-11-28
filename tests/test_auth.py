from fastapi.testclient import TestClient


def register_user(
    client: TestClient,
    *,
    email: str = "user@example.com",
    password: str = "test123",
    name: str = "Test User",
):
    """Helper to register a user."""
    return client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )


def test_register_creates_user_and_sets_cookie(client: TestClient):
    response = register_user(client, email="user1@example.com")
    assert response.status_code == 201

    data = response.json()
    # RegisterResponse only exposes the user ID
    assert "id" in data
    assert data["id"] is not None

    # JWT cookie should be set
    assert "token" in response.cookies


def test_register_with_existing_email_returns_400(client: TestClient):
    email = "duplicate@example.com"

    first = register_user(client, email=email)
    assert first.status_code == 201

    second = register_user(client, email=email)
    assert second.status_code == 400
    assert second.json()["detail"] == "User already exists"


def test_login_me_and_logout_flow(client: TestClient):
    email = "flow@example.com"
    password = "test123"

    # Register user
    register_user(client, email=email, password=password)

    # Login
    login_resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200

    data = login_resp.json()
    assert data["email"] == email
    assert "id" in data
    assert "token" in login_resp.cookies

    # /auth/me should return the current user while authenticated
    me_resp = client.get("/auth/me")
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == email
    assert me_data["name"] == "Test User"

    # Logout clears the cookie
    logout_resp = client.get("/auth/logout")
    assert logout_resp.status_code == 204

    # After logout, /auth/me should be unauthorized
    me_after_logout = client.get("/auth/me")
    assert me_after_logout.status_code == 401
    assert me_after_logout.json()["detail"] in {
        "Not authenticated",
        "Invalid token",
        "Expired token",
        "User not found",
    }


def test_login_with_invalid_credentials_returns_401(client: TestClient):
    email = "invalid-login@example.com"
    password = "test123"

    # Create a valid user
    register_user(client, email=email, password=password)

    # Wrong password
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": "wrong-password"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_me_unauthenticated_returns_401(client: TestClient):
    # No login / no token cookie
    resp = client.get("/auth/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"
