from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Optional

load_dotenv()


class Config(BaseModel):
    class Auth(BaseModel):
        cookie: str = os.getenv('COOKIE', '')

    class Proxy(BaseModel):
        http: str = os.getenv('HTTP_PROXY', '')
        https: str = os.getenv('HTTPS_PROXY', '')

    class Chat(BaseModel):
        chat_model: str = os.getenv('CHAT_MODEL', 'gpt-4')

    auth: Auth = Auth()
    proxy: Proxy = Proxy()
    chat: Chat = Chat()
    timeout: Optional[int] = int(os.getenv('TIME_OUT', 60))


def get_config() -> Config:
    return Config()
