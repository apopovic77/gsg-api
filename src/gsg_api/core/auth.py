"""
API Key Authentication
"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from .config import get_settings

# Header name for API key
API_KEY_HEADER = APIKeyHeader(name="x-api-key", auto_error=False)


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Verify the API key from x-api-key header.

    Raises:
        HTTPException: If API key is missing or invalid

    Returns:
        The validated API key
    """
    settings = get_settings()

    # Check if API key authentication is configured
    if not settings.valid_api_keys:
        # No keys configured = auth disabled (development mode)
        return "dev-mode"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide 'x-api-key' header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key not in settings.valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return api_key
