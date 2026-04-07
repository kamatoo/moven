from __future__ import annotations

from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegister
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(self, payload: UserRegister) -> User:
        if self.repository.get_by_email(payload.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        return self.repository.create(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=UserRole.MEMBER,
            is_active=True,
        )

    def authenticate_user(self, email: str, password: str) -> str:
        user = self.repository.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )

        return create_access_token(subject=user.email, role=user.role.value)

    def create_user(self, payload: UserCreate) -> User:
        if self.repository.get_by_email(payload.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        return self.repository.create(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role,
            is_active=payload.is_active,
        )
