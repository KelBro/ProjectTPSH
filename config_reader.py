from pydantic import SecretStr, BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
