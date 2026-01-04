import pytest
from app.services.utility_service import UtilityService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_database_version(utility_service: UtilityService):
    """
    Test that utility service can retrieve database version.
    This test demonstrates:
    - Service layer testing
    - Database connectivity
    - Async test patterns
    """
    version = await utility_service.get_database_version()
    
    assert isinstance(version, str), "Database version should be a string"
    assert len(version) > 0, "Database version should not be empty"
    # MySQL version typically starts with a number
    assert version[0].isdigit() or version.startswith("8.") or version.startswith("5."), \
        "Database version should look like a MySQL version"

