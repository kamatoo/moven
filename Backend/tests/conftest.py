from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_auth_service, get_db_session, get_user_service
from app.core.security import create_access_token
from app.db.base import Base
from app.db.models.user import User, UserRole
from app.main import app
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegister
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from app.services.user_service import UserService

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def user_service(db_session: Session) -> UserService:
    return UserService(repository=UserRepository(db_session))


@pytest.fixture
def auth_service(db_session: Session) -> AuthService:
    return AuthService(repository=UserRepository(db_session))


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db_session() -> Generator[Session, None, None]:
        yield db_session

    def override_get_user_service() -> UserService:
        return UserService(repository=UserRepository(db_session))

    def override_get_auth_service() -> AuthService:
        return AuthService(repository=UserRepository(db_session))

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_user_service] = override_get_user_service
    app.dependency_overrides[get_auth_service] = override_get_auth_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def seeded_user(auth_service: AuthService):
    return auth_service.register_user(
        UserRegister(name="Ada Lovelace", email="ada@example.com", password="secret123")
    )


@pytest.fixture
def admin_user(user_service: UserService):
    return user_service.create_user(
        UserCreate(
            name="Admin User",
            email="admin@example.com",
            password="secret123",
            role=UserRole.ADMIN,
            is_active=True,
        )
    )


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token(subject=admin_user.email, role=admin_user.role.value)


@pytest.fixture
def user_token(seeded_user: User) -> str:
    return create_access_token(subject=seeded_user.email, role=seeded_user.role.value)
