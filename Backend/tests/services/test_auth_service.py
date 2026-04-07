from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.schemas.auth import UserRegister
from app.schemas.user import UserUpdate


def test_auth_service_registers_user(auth_service):
    user = auth_service.register_user(
        UserRegister(
            name="Linus Torvalds",
            email="linus@example.com",
            password="secret123",
        )
    )

    assert user.id is not None
    assert user.email == "linus@example.com"
    assert user.password_hash != "secret123"


def test_auth_service_rejects_duplicate_email(auth_service):
    auth_service.register_user(
        UserRegister(
            name="Margaret Hamilton",
            email="margaret@example.com",
            password="secret123",
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        auth_service.register_user(
            UserRegister(
                name="Duplicate",
                email="margaret@example.com",
                password="secret123",
            )
        )

    assert exc_info.value.status_code == 409


def test_auth_service_authenticates_existing_user(auth_service, seeded_user):
    token = auth_service.authenticate_user(seeded_user.email, "secret123")

    assert isinstance(token, str)
    assert token


def test_auth_service_rejects_wrong_password(auth_service, seeded_user):
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate_user(seeded_user.email, "wrong-password")

    assert exc_info.value.status_code == 401


def test_user_service_updates_existing_user(user_service, seeded_user):
    updated = user_service.update_user(
        seeded_user.id,
        UserUpdate(name="Ada Byron", email="ada.byron@example.com"),
    )

    assert updated is not None
    assert updated.name == "Ada Byron"
    assert updated.email == "ada.byron@example.com"
