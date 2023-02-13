from pydantic import BaseSettings, SecretStr, BaseModel, validator

def get_ngrok_url():
    import requests
    ngork_url = 'http://localhost:4040/api/tunnels'
    return requests.get(ngork_url).json()['tunnels'][0]['public_url']


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
    webhook_port: int = 8080

    class Config:
        env_prefix = 'tg_'

    @validator('webhook_url')
    def webhook_url_validator(cls, v):
        if v and not v.startswith('https://'):
            if v == 'ngork':
                return get_ngrok_url()
            raise ValueError('Webhook url must start with https://')
        return v


class Config(BaseSettings):
    tg: TGConfig = TGConfig()
    mongo: MongoConfig = MongoConfig()
    gs_creds: str = 'creds.json'
