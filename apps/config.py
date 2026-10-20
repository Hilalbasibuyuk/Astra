from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "astra"
    postgres_user: str = "astra"
    postgres_password: str = "astra"

    questdb_host: str = "localhost"
    questdb_http_port: int = 9000
    questdb_ilp_port: int = 9009
    questdb_pg_port: int = 8812

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ollama_timeout_seconds: float = 120.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()