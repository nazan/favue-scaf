from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.db.tables import metadata  # Import your metadata

# Load Alembic config
config = context.config
fileConfig(config.config_file_name)

# Define target metadata (used for autogenerate)
target_metadata = metadata

# Read database URL from alembic.ini
DATABASE_URL = config.get_main_option("sqlalchemy.url")

# Create a sync engine for Alembic migrations
sync_engine = create_engine(
    DATABASE_URL,
    poolclass=pool.NullPool,
    future=True
)


def run_migrations_online():
    """Run migrations in 'online' mode using a synchronous engine."""
    with sync_engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Execute migrations
run_migrations_online()

