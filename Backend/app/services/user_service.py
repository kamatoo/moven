from __future__ import annotations

from fastapi import HTTPException, status

from app.core.security import hash_password
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def list_users(self) -> list[User]:
        return self.repository.list()

    def get_user(self, user_id: int) -> User | None:
        return self.repository.get(user_id)

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

    def update_user(self, user_id: int, payload: UserUpdate) -> User | None:
        user = self.repository.get(user_id)
        if user is None:
            return None

        if payload.email and payload.email != user.email:
            existing = self.repository.get_by_email(payload.email)
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email is already registered",
                )

        password_hash = hash_password(payload.password) if payload.password else None

        return self.repository.update(
            user,
            name=payload.name,
            email=payload.email,
            password_hash=password_hash,
            role=payload.role,
            is_active=payload.is_active,
        )

    def delete_user(self, user_id: int) -> bool:
        user = self.repository.get(user_id)
        if user is None:
            return False
        self.repository.delete(user)
        return True
