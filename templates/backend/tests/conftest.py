import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.tables import metadata
from app.db.session import db_session, clean_database_url
from app.main import app
from app.service_init import get_utility_service
from app.config import Settings, settings
import asyncio
import logging

def pytest_configure():
    if settings.exec_env != 'testing':
        pytest.exit(f"Tests aborted! EXEC_ENV={settings.exec_env} (expected 'testing').")

@pytest.fixture
def settings_factory():
    """Factory function to create settings instance after modifying env variables."""
    def _create_settings():
        return Settings()
    
    return _create_settings


@pytest.fixture(scope="module")
def event_loop():
    """Override the default function-scoped event_loop to module scope."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def engine(event_loop):
    """Create async engine within the event loop context."""
    # Clean the URL to remove unsupported parameters like ssl_disabled
    database_url = clean_database_url(settings.database_url)
    
    # Create engine within the event loop context
    eng = create_async_engine(
        database_url, 
        echo=False,
        isolation_level="READ COMMITTED"  # Ensure transaction isolation
    )
    
    yield eng


@pytest.fixture(scope="module")
def TestingSessionLocal(engine):
    """Create async session factory."""
    return sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )


# Override FastAPI's get_db dependency
@pytest.fixture(scope="function")
async def test_db_session(TestingSessionLocal):
    """Provide a database session and ensure proper cleanup."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            # Always rollback to undo all changes made during the test
            await session.rollback()
            await session.close()  # Explicitly close the session

@pytest.fixture
def test_logger():
    logger = logging.getLogger("app-test")
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

@pytest.fixture
def utility_service(test_db_session: AsyncSession, test_logger):
    """Fixture that provides an instance of UtilityService with a test database session."""
    return get_utility_service(test_db_session, test_logger)

@pytest.fixture(scope="module", autouse=True)
async def setup_db(engine):
    """Recreate the test database before each module's tests."""
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    
    # Dispose of the engine at the end of each module
    await engine.dispose()

# Apply the database override to the FastAPI app
app.dependency_overrides[db_session] = test_db_session

