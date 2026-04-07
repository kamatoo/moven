from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.session import SessionLocal, check_database_connection
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.bootstrap_service import BootstrapService

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting application", extra={"app_name": settings.app_name})
    db = SessionLocal()
    try:
        bootstrap_service = BootstrapService(
            auth_service=AuthService(repository=UserRepository(db)),
            user_repository=UserRepository(db),
        )
        bootstrap_service.seed_admin()
    finally:
        db.close()
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

if settings.cors_allow_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
def readiness() -> dict[str, str]:
    try:
        check_database_connection()
    except Exception as exc:  # pragma: no cover
        logger.exception("Database readiness check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready",
        ) from exc
    return {"status": "ready"}
