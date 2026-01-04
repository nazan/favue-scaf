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


settings = Settings()  # type: ignore

