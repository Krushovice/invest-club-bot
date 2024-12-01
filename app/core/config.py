from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,

    )

    bot_token: str

    pay_terminal_key: str
    pay_secret: str

    channel_link: str




settings = Settings()