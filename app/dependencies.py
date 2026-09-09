from typing import Annotated
from fastapi import Header, HTTPException, status, Query

# My secret API key for authentication on write operations
VALID_API_KEY = "james-apf3.0-trainee"


def require_api_key(x_api_key: Annotated[str, Header()]) -> str:
    """Dependency to validate the X-API-Key header."""
    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return x_api_key


class PaginationParams:
    """Class-based dependency for standard query pagination."""
    def __init__(
        self,
        offset: int = Query(default=0, ge=0, description="Items to skip"),
        limit: int = Query(default=10, le=100, description="Max items to return"),
    ):
        self.offset = offset
        self.limit = limit