from sqlalchemy import MetaData, Table, Column
from sqlalchemy import Integer, String, DateTime, Boolean
from datetime import datetime

metadata = MetaData()

alembic_version = Table(
    'alembic_version',
    metadata,
    Column('version_num', String(32), nullable=False, primary_key=True),
)

users = Table(
    'users',
    metadata,
    Column('id', Integer, nullable=False, primary_key=True, autoincrement=True),
    Column('username', String(100), nullable=False, unique=True),
    Column('email', String(255), nullable=False, unique=True),
    Column('password_hash', String(500), nullable=False),
    Column('is_active', Boolean, nullable=False, default=True),
    Column('email_verified_at', DateTime, nullable=True),
    Column('email_verification_token', String(255), nullable=True),
    Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
    Column('updated_at', DateTime, nullable=False, default=datetime.utcnow),
)
