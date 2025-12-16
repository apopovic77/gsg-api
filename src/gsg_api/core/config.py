"""
GSG API Configuration
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    api_title: str = "GSG API"
    api_description: str = "Gravity Sports Group Product API - O'Neal, Lezyne, EVS & more"
    api_version: str = "1.0.0"

    # Authentication
    api_keys: str = ""  # Comma-separated list of valid API keys

    # Database
    mssql_host: str = "192.168.2.63"
    mssql_port: int = 1433
    mssql_database: str = "lius"
    mssql_user: str = ""
    mssql_password: str = ""

    # CORS
    cors_origins: str = "*"

    @property
    def valid_api_keys(self) -> List[str]:
        """Parse comma-separated API keys"""
        if not self.api_keys:
            return []
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins"""
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def mssql_connection_string(self) -> str:
        """Build MSSQL connection string for pyodbc"""
        return (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.mssql_host},{self.mssql_port};"
            f"DATABASE={self.mssql_database};"
            f"UID={self.mssql_user};"
            f"PWD={self.mssql_password};"
            f"TrustServerCertificate=yes"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
