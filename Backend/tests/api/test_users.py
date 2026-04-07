from __future__ import annotations


def test_admin_can_create_user(client, admin_token):
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Grace Hopper",
            "email": "grace@example.com",
            "password": "supersecret123",
            "role": "member",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "grace@example.com"
    assert body["role"] == "member"


def test_member_cannot_list_users(client, seeded_user, user_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_can_list_users(client, admin_user, seeded_user, admin_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {user["email"] for user in body} == {"admin@example.com", "ada@example.com"}


def test_user_can_get_own_profile_by_id(client, seeded_user, user_token):
    response = client.get(
        f"/api/v1/users/{seeded_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == seeded_user.email


def test_user_cannot_get_other_user(client, admin_user, user_token):
    response = client.get(
        f"/api/v1/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


def test_user_can_update_own_profile_but_not_role(client, seeded_user, user_token):
    response = client.put(
        f"/api/v1/users/{seeded_user.id}",
        json={
            "name": "Ada Byron",
            "email": "ada.byron@example.com",
            "role": "admin",
            "is_active": False,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Ada Byron"
    assert body["email"] == "ada.byron@example.com"
    assert body["role"] == "member"
    assert body["is_active"] is True


def test_admin_can_update_role(client, seeded_user, admin_token):
    response = client.put(
        f"/api/v1/users/{seeded_user.id}",
        json={"role": "admin", "is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "admin"
    assert body["is_active"] is False


def test_user_can_delete_self(client, seeded_user, user_token):
    response = client.delete(
        f"/api/v1/users/{seeded_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 204


def test_missing_token_is_unauthorized(client):
    response = client.get("/api/v1/users")

    assert response.status_code == 401
