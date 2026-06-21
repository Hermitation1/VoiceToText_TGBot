from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    owner_id: int
    proxy_url: str | None = None
    # hf_token: str
    # http_proxy: str
    # https_proxy: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
