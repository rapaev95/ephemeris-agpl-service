"""Meta endpoints (health, version, source) - no authentication required."""

from fastapi import APIRouter
from app.core.versioning import get_version_info, get_source_info
from app.models.responses import VersionResponse, SourceResponse

router = APIRouter()


@router.get("/health", tags=["meta"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Simple health status
    """
    return {"ok": True}


@router.get("/v1/version", response_model=VersionResponse, tags=["meta"])
async def get_version() -> VersionResponse:
    """
    Get version and build information.

    Returns:
        Version information including git commit, build tag, and build time
    """
    version_info = get_version_info()
    return VersionResponse(**version_info)


@router.get("/v1/source", response_model=SourceResponse, tags=["meta"])
async def get_source() -> SourceResponse:
    """
    Get source code information for AGPL compliance.

    Returns:
        Source code information including repository URL, tag, and commit
    """
    source_info = get_source_info()
    return SourceResponse(**source_info)
