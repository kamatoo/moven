from __future__ import annotations

from sqlalchemy import select

from app.db.models.user import User, UserRole
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def list(self) -> list[User]:
        return super().list(order_by=User.id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole,
        is_active: bool = True,
    ) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        return self.add(user)

    def update(
        self,
        user: User,
        *,
        name: str | None,
        email: str | None,
        password_hash: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> User:
        return super().update(
            user,
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
