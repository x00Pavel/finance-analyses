from pathlib import Path
from typing import Optional

import requests
from pydantic import BaseSettings, SecretStr, validator
from tenacity import retry, stop_after_attempt

curr_dir = Path(__file__).parent

try:
    from dotenv import load_dotenv

    assert load_dotenv(curr_dir.parent / ".env")
    print("Loaded .env file")
except AssertionError:
    print("No .env file found")
except ModuleNotFoundError:
    print("No .env file found")


@retry(stop=stop_after_attempt(5))
def get_ngrok_url():
    ngork_url = "http://ngrok:4040/api/tunnels"
    url: str = requests.get(ngork_url).json()["tunnels"][0]["public_url"]
    return url.replace("http://", "https://")


class MongoConfig(BaseSettings):
    user: str
    passwd: SecretStr
    host: str = "localhost"
    port: int = 27017
    db: str = "fin_bot"

    class Config:
        env_prefix = "mongo_"


class TGConfig(BaseSettings):
    token: SecretStr
    webhook_url: str = None
    webhook_port: int = 8080

    class Config:
        env_prefix = "tg_"

    @validator("webhook_url")
    def webhook_url_validator(cls, v):
        v = v.strip()
        if v:
            if v == "ngrok":
                return get_ngrok_url()
            elif v.startswith("http://"):
                return v.replace("http://", "https://")
            elif v.startswith("https://"):
                return v
            raise ValueError(f"Webhook url {v} must start with https://")


class GSConfig(BaseSettings):
    creds: str
    file_prefix: str = "testing"

    class Config:
        env_prefix = "gs_"


class Config(BaseSettings):
    tg: TGConfig = TGConfig()
    mongo: MongoConfig = MongoConfig()
    gs: Optional[GSConfig] = None
