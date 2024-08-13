from pydantic_settings import BaseSettings
from lume_py.endpoints.sdk.api_client import Lume
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    lume_api_key: Optional[str] = None
    client: Optional[Lume] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.lume_api_key:
            self.client = Lume(api_key=self.lume_api_key)

    def set_api_key(self, api_key: str):
        self.lume_api_key = api_key
        self.client = Lume(api_key=self.lume_api_key)

@lru_cache()
def get_settings() -> Settings:
    return Settings()
