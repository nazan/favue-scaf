from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.db.tables import metadata  # Import your metadata
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import os

# Load Alembic config
config = context.config
fileConfig(config.config_file_name)

# Define target metadata (used for autogenerate)
target_metadata = metadata

# mysql-connector-python doesn't support ssl_disabled parameter, so we remove it from the URL
# Also convert async drivers (aiomysql) to sync drivers (mysqlconnector) for Alembic
def clean_database_url(url: str) -> str:
    """Convert async database URL to sync and remove unsupported parameters for mysql-connector-python."""
    # Convert async drivers to sync drivers for Alembic
    url = url.replace("+aiomysql", "+mysqlconnector")
    
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Remove unsupported parameters for mysql-connector-python
    unsupported_params = ['ssl_disabled']
    for param in unsupported_params:
        query_params.pop(param, None)
    
    # Reconstruct URL without unsupported parameters
    new_query = urlencode(query_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)

# Read database URL from environment variable (for testing) or alembic.ini
DATABASE_URL = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

# Clean the URL to remove unsupported parameters
cleaned_url = clean_database_url(DATABASE_URL)

# Create a sync engine for Alembic migrations
sync_engine = create_engine(
    cleaned_url,
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

