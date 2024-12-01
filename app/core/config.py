from aiogram.enums import ParseMode
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, BaseModel


class TelegramConfig(BaseModel):
    token: str
    parse_mode: ParseMode = ParseMode.HTML


class DataBaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 20
    max_overflow: int = 10


class PaymentConfig(BaseModel):
    terminal_key: str
    secret: str


class AdminConfig(BaseModel):
    admin_id: int
    debug: bool = True
    channel_link: str




class Settings(BaseSettings):

    main: AdminConfig

    db: DataBaseConfig

    bot: TelegramConfig

    pay: PaymentConfig

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_nested_delimiter="__",
        env_prefix="CONFIG__",
        env_file_encoding="utf-8",
        validate_default=False,
    )


settings = Settings()