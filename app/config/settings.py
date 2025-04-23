from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    DB_HOST_TEST: str
    DB_PORT_TEST: int
    DB_USERNAME_TEST: str
    DB_PASSWORD_TEST: str
    DB_DATABASE_TEST: str
    CA_CERT_PATH: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables

    def validate_env(self):
        """Validate that all required environment variables are set."""
        missing = []
        for field in self.__fields__:
            if getattr(self, field) is None:
                missing.append(field)
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        # Validate CA certificate file existence
        ca_cert_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', self.CA_CERT_PATH))
        if not os.path.exists(ca_cert_path):
            raise FileNotFoundError(f"CA certificate file not found at: {ca_cert_path}")

@lru_cache
def get_settings():
    settings = Settings()
    settings.validate_env()
    return settings

settings = get_settings()