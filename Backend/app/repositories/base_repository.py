from __future__ import annotations

from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.base import Base


class BaseRepository[ModelT: Base]:
    model: type[ModelT]

    def __init__(self, db: Session):
        self.db = db

    def get(self, entity_id: Any) -> ModelT | None:
        return self.db.get(self.model, entity_id)

    def list(self, *, order_by=None) -> list[ModelT]:
        stmt: Select[tuple[ModelT]] = select(self.model)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        return list(self.db.scalars(stmt))

    def add(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, instance: ModelT, **changes: Any) -> ModelT:
        for field, value in changes.items():
            if value is not None:
                setattr(instance, field, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.db.delete(instance)
        self.db.commit()
