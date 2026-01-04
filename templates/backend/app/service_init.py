from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import logging

from app.db.session import db_session
from app.log_setup import get_app_logger
from app.core.di import ServiceContainer, ServiceLifetime
from app.services.utility_service import UtilityService


# Global container instance
_container = ServiceContainer()


def _register_services_once() -> None:
    # Logger as singleton
    _container.register(
        "logger",
        lambda _c, _s: get_app_logger(),
        lifetime=ServiceLifetime.SINGLETON,
    )

    # UtilityService as scoped (needs db per-request), depends on logger
    def _mk_utility(c: ServiceContainer, scope: dict) -> UtilityService:
        db: AsyncSession = scope["db"]
        logger: logging.Logger = c.resolve("logger", scope)
        return UtilityService(db, logger)

    _container.register(
        "utility",
        _mk_utility,
        lifetime=ServiceLifetime.SCOPED,
        depends_on=["logger"],
    )


# Ensure base registrations exist
_register_services_once()


def _scope(db: AsyncSession, logger: logging.Logger) -> dict:
    return {"db": db, "logger": logger}


def get_utility_service(
    db: AsyncSession = Depends(db_session),
    logobj: logging.Logger = Depends(get_app_logger),
) -> UtilityService:
    """Get utility service. Can be used with FastAPI Depends() or called directly."""
    return _container.resolve("utility", _scope(db, logobj))

