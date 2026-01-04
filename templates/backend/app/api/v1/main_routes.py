from fastapi import APIRouter, Depends
from app.services.utility_service import UtilityService
from app.service_init import get_utility_service
from app.schemas.utility_schema import DatabaseVersionResponse
from app.log_setup import get_app_logger
import logging

router = APIRouter(prefix="/api")


@router.get("/dbversion", response_model=DatabaseVersionResponse)
async def get_db_version(
    utility_service: UtilityService = Depends(get_utility_service),
    logger: logging.Logger = Depends(get_app_logger)
):
    """
    Get database version.
    This endpoint demonstrates:
    - Pydantic response models
    - Service layer usage via dependency injection
    - End-to-end connectivity from API to database
    """
    version = await utility_service.get_database_version()
    logger.info(f"Database version requested: {version}")
    return DatabaseVersionResponse(version=version)

