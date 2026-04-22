from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import logging

from app.db.session import db_session
from app.log_setup import get_app_logger
from app.core.di import ServiceContainer, ServiceLifetime
from app.services.utility_service import UtilityService
from app.services.user_service import UserService
from app.services.email_service import EmailService, LogEmailTransport


# Global container instance
_container = ServiceContainer()


def _register_services_once() -> None:
    # Logger as singleton
    _container.register(
        "logger",
        lambda _c, _s: get_app_logger(),
        lifetime=ServiceLifetime.SINGLETON,
    )

    def _mk_email(c: ServiceContainer, scope: dict) -> EmailService:
        logger: logging.Logger = c.resolve("logger", scope)
        transport = LogEmailTransport(logger)
        return EmailService(transport, logger)

    _container.register(
        "email",
        _mk_email,
        lifetime=ServiceLifetime.SINGLETON,
        depends_on=["logger"],
    )

    # UtilityService as scoped (needs db per-request), depends on logger
    def _mk_utility(c: ServiceContainer, scope: dict) -> UtilityService:
        db: AsyncSession = scope["db"]
        logobj: logging.Logger = c.resolve("logger", scope)
        return UtilityService(db, logobj)

    _container.register(
        "utility",
        _mk_utility,
        lifetime=ServiceLifetime.SCOPED,
        depends_on=["logger"],
    )

    def _mk_user(c: ServiceContainer, scope: dict) -> UserService:
        db: AsyncSession = scope["db"]
        email_svc: EmailService = c.resolve("email", scope)
        logobj: logging.Logger = c.resolve("logger", scope)
        return UserService(db, email_svc, logobj)

    _container.register(
        "user",
        _mk_user,
        lifetime=ServiceLifetime.SCOPED,
        depends_on=["email", "logger"],
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


def get_user_service(
    db: AsyncSession = Depends(db_session),
    logobj: logging.Logger = Depends(get_app_logger),
) -> UserService:
    return _container.resolve("user", _scope(db, logobj))
