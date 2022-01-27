from os import path

from pydantic import BaseSettings

DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    application_name: str = "account-connections"
    environment: str = "unknown"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_port: int
    server_prefix: str = ""

    database_url: str

    token_url: str
    json_web_token_secret: str
    json_web_token_algorithm: str

    robinhood_client_id: str
    robinhood_device_token: str

    encryption_secret_key: str

    asset_update_task_frequency: int = 3600 * 24
    refresh_tokens_task_frequency: int = 3600 * 24

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
