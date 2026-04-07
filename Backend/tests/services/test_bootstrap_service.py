from __future__ import annotations

from app.core.config import settings
from app.db.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.bootstrap_service import BootstrapService


def test_seed_admin_creates_admin_user(db_session, monkeypatch):
    monkeypatch.setattr(settings, "seed_admin_enabled", True)
    monkeypatch.setattr(settings, "seed_admin_name", "Seed Admin")
    monkeypatch.setattr(settings, "seed_admin_email", "seed-admin@example.com")
    monkeypatch.setattr(settings, "seed_admin_password", "seedpassword123")

    repository = UserRepository(db_session)
    bootstrap_service = BootstrapService(
        auth_service=AuthService(repository=repository),
        user_repository=repository,
    )

    bootstrap_service.seed_admin()

    admin = repository.get_by_email("seed-admin@example.com")
    assert admin is not None
    assert admin.role == UserRole.ADMIN
    assert admin.is_active is True


def test_seed_admin_is_idempotent(db_session, monkeypatch):
    monkeypatch.setattr(settings, "seed_admin_enabled", True)
    monkeypatch.setattr(settings, "seed_admin_name", "Seed Admin")
    monkeypatch.setattr(settings, "seed_admin_email", "seed-admin@example.com")
    monkeypatch.setattr(settings, "seed_admin_password", "seedpassword123")

    repository = UserRepository(db_session)
    bootstrap_service = BootstrapService(
        auth_service=AuthService(repository=repository),
        user_repository=repository,
    )

    bootstrap_service.seed_admin()
    bootstrap_service.seed_admin()

    users = repository.list()
    assert len(users) == 1
