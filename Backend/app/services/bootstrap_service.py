from __future__ import annotations

from app.core.config import settings
from app.core.logging import get_logger
from app.db.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

logger = get_logger(__name__)


class BootstrapService:
    def __init__(self, auth_service: AuthService, user_repository: UserRepository):
        self.auth_service = auth_service
        self.user_repository = user_repository

    def seed_admin(self) -> None:
        if not settings.seed_admin_enabled:
            logger.info("Seed admin disabled")
            return

        existing_admin = self.user_repository.get_by_email(settings.seed_admin_email)
        if existing_admin is not None:
            logger.info("Seed admin already exists", extra={"email": settings.seed_admin_email})
            return

        self.auth_service.create_user(
            UserCreate(
                name=settings.seed_admin_name,
                email=settings.seed_admin_email,
                password=settings.seed_admin_password,
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        logger.info("Seed admin created", extra={"email": settings.seed_admin_email})
