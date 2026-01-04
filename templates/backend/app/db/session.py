from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from app.config import settings

# aiomysql doesn't support ssl_disabled parameter, so we remove it from the URL
def clean_database_url(url: str) -> str:
    """Remove unsupported parameters from database URL for aiomysql."""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Remove unsupported parameters for aiomysql
    unsupported_params = ['ssl_disabled']
    for param in unsupported_params:
        query_params.pop(param, None)
    
    # Reconstruct URL without unsupported parameters
    new_query = urlencode(query_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)

# Create async engine with cleaned URL
database_url = clean_database_url(settings.database_url)
engine = create_async_engine(database_url, echo=settings.echo_sql, future=True)

SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def db_session():
    async with SessionLocal() as session:
        yield session

