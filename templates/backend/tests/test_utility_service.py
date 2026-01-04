import pytest
from app.services.utility_service import UtilityService
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings


@pytest.mark.asyncio
async def test_get_database_version(setup_db, utility_service: UtilityService, test_logger):
    """
    Test that utility service can retrieve database version.
    This test demonstrates:
    - Service layer testing
    - Database connectivity
    - Async test patterns
    """
    # test_logger.info(settings.database_url)
    
    version = await utility_service.get_database_version()
    
    assert isinstance(version, str), "Database version should be a string"
    assert len(version) > 0, "Database version should not be empty"
    # MySQL version typically starts with a number
    assert version[0].isdigit() or version.startswith("8.") or version.startswith("5."), \
        "Database version should look like a MySQL version"

