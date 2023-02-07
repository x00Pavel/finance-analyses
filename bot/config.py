from pydantic import BaseSettings, SecretStr, BaseModel


class MongoConfig(BaseSettings):
    user: str
    passwd: SecretStr
    host: str = 'localhost'
    port: int = 27017
    db: str = 'fin_bot'

    class Config:
        env_prefix = 'mongo_'


class TGConfig(BaseSettings):
    token: SecretStr
    webhook_url: str = None

    class Config:
        env_prefix = 'tg_'


class Config(BaseSettings):
    tg: TGConfig = TGConfig()
    mongo: MongoConfig = MongoConfig()
    gs_creds: str = 'creds.json'
