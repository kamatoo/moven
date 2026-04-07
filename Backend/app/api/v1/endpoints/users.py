from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db_session, require_admin_user
from app.db.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(db: Annotated[Session, Depends(get_db_session)]) -> UserService:
    return UserService(repository=UserRepository(db))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
CurrentUserDep = Annotated[User, Depends(get_current_active_user)]
AdminUserDep = Annotated[User, Depends(require_admin_user)]


def ensure_user_access(target_user_id: int, current_user: User) -> None:
    if current_user.role != UserRole.ADMIN and current_user.id != target_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("", response_model=list[UserRead])
def list_users(service: UserServiceDep, _: AdminUserDep) -> list[UserRead]:
    return service.list_users()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    service: UserServiceDep,
    _: AdminUserDep,
) -> UserRead:
    return service.create_user(payload)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: UserServiceDep, current_user: CurrentUserDep) -> UserRead:
    ensure_user_access(user_id, current_user)
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserServiceDep,
    current_user: CurrentUserDep,
) -> UserRead:
    ensure_user_access(user_id, current_user)
    if current_user.role != UserRole.ADMIN:
        payload = payload.model_copy(update={"role": None, "is_active": None})
    user = service.update_user(user_id, payload)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, service: UserServiceDep, current_user: CurrentUserDep) -> None:
    ensure_user_access(user_id, current_user)
    deleted = service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
