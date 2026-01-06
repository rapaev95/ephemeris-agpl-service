"""Authentication middleware for API endpoints."""

import os
from typing import Optional
from fastapi import Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .errors import raise_unauthorized

# Security scheme for OpenAPI docs
security = HTTPBearer(auto_error=False)


def get_api_keys() -> list[str]:
    """
    Get API keys from environment variables.

    Supports both AGPL_SERVICE_API_KEYS (comma-separated) and AGPL_SERVICE_API_KEY (single).

    Returns:
        List of API keys
    """
    keys_str = os.getenv("AGPL_SERVICE_API_KEYS") or os.getenv("AGPL_SERVICE_API_KEY")
    if not keys_str:
        return []

    # Split by comma and strip whitespace
    keys = [key.strip() for key in keys_str.split(",") if key.strip()]
    return keys


def verify_token(token: str) -> bool:
    """
    Verify if token is valid.

    Args:
        token: Bearer token to verify

    Returns:
        True if token is valid
    """
    api_keys = get_api_keys()
    if not api_keys:
        # If no keys configured, allow all (development mode)
        # In production, this should be an error
        return True

    return token in api_keys


async def require_auth(
    authorization: Optional[HTTPAuthorizationCredentials] = Header(None),
) -> str:
    """
    Dependency for protected endpoints that require authentication.

    Args:
        authorization: Authorization header from request

    Returns:
        The verified token

    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise_unauthorized("Missing authorization header")

    token = authorization.credentials
    if not verify_token(token):
        raise_unauthorized("Invalid authorization token")

    return token
