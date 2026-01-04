from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
import logging


class UtilityService:
    """Example service demonstrating service layer pattern with DI."""

    def __init__(self, db: AsyncSession, logger: Optional[logging.Logger] = None):
        self.db = db
        self.logger = logger

    async def get_database_version(self) -> str:
        """
        Get MySQL database version.
        This method demonstrates:
        - Service layer business logic
        - Database access via SQLAlchemy Core (no ORM)
        - Dependency injection pattern
        """
        try:
            result = await self.db.execute(text("SELECT VERSION() as version"))
            row = result.fetchone()
            if row:
                version = row[0]
                if self.logger:
                    self.logger.info(f"Database version retrieved: {version}")
                return version
            return "Unknown"
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error retrieving database version: {e}")
            raise

