from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OrdersSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)
    database_url: str
    migration_database_url: str
    jwt_secret: str = Field(default="HS256")
    jwt_algorithm: str


settings = OrdersSettings()
