from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_ignore_empty=True, env_nested_delimiter='__')

    exec_env: str = "development"
    database_url: str
    echo_sql: bool = False
    test: bool = False
    project_name: str = "${PROJECT_NAME}"
    log_level: str = "DEBUG"
    version: str = "1.0.0"

    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 10080  # 7 days

    # Transactional email (verification links). Use gateway URL in dev, e.g. http://localhost
    email_from_address: str = "noreply@example.com"
    email_from_name: str = "${PROJECT_NAME}"
    email_verify_base_url: str = "http://localhost"

    internal_cron_secret: str = ""
    redis_url: str = "redis://redis:6379"
    redis_key_prefix: str = "${PROJECT_NAME}:"


settings = Settings()  # type: ignore
