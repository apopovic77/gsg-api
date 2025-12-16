"""Core module - config, auth, database"""
from .config import get_settings, Settings
from .auth import verify_api_key
from .database import db, DatabaseManager

__all__ = ["get_settings", "Settings", "verify_api_key", "db", "DatabaseManager"]
