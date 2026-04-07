from __future__ import annotations


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Grace Hopper",
            "email": "grace@example.com",
            "password": "supersecret123",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "grace@example.com"
    assert body["role"] == "member"
    assert body["is_active"] is True


def test_login_returns_bearer_token(client, seeded_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": seeded_user.email, "password": "secret123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert response.cookies.get("access_token")


def test_me_returns_current_user(client, user_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "ada@example.com"


def test_me_returns_current_user_from_cookie(client, seeded_user):
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": seeded_user.email, "password": "secret123"},
    )

    assert login_response.status_code == 200

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "ada@example.com"


def test_login_rejects_invalid_password(client, seeded_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": seeded_user.email, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_logout_clears_auth_cookie(client, seeded_user):
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": seeded_user.email, "password": "secret123"},
    )

    assert login_response.status_code == 200

    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 204
    assert "access_token=" in response.headers["set-cookie"]
    assert "Max-Age=0" in response.headers["set-cookie"]
