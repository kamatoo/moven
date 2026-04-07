from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.models.user import User, UserRole
from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPayload
from app.services.auth_service import AuthService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_service(db: Annotated[Session, Depends(get_db_session)]) -> UserService:
    return UserService(repository=UserRepository(db))


def get_auth_service(db: Annotated[Session, Depends(get_db_session)]) -> AuthService:
    return AuthService(repository=UserRepository(db))


def get_current_user(
    bearer_token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db_session)],
    cookie_token: Annotated[str | None, Cookie(alias=settings.auth_cookie_name)] = None,
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = bearer_token or cookie_token
    if token is None:
        raise credentials_error

    try:
        payload = decode_token(token)
        token_data = TokenPayload.model_validate(payload)
    except (InvalidTokenError, ValueError) as exc:
        raise credentials_error from exc

    user = UserRepository(db).get_by_email(token_data.sub)
    if user is None:
        raise credentials_error
    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


def require_admin_user(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
