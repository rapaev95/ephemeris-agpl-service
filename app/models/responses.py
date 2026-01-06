"""Pydantic models for API responses."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PositionsMeta(BaseModel):
    """Metadata for positions response."""

    engine: str = Field(default="swisseph", description="Calculation engine")
    sidereal: bool = Field(default=False, description="Sidereal zodiac used")


class PositionsResponse(BaseModel):
    """Response model for positions calculation."""

    jd_ut: float = Field(..., description="Julian Day in UT")
    positions: Dict[str, float] = Field(..., description="Body positions in degrees")
    meta: PositionsMeta = Field(..., description="Calculation metadata")


class HousesAngles(BaseModel):
    """Angles (Ascendant, MC) for houses response."""

    asc: float = Field(..., description="Ascendant in degrees")
    mc: float = Field(..., description="MC (Midheaven) in degrees")


class HousesResponse(BaseModel):
    """Response model for houses calculation."""

    jd_ut: float = Field(..., description="Julian Day in UT")
    house_system: str = Field(..., description="House system code")
    cusps: List[float] = Field(..., description="House cusps (13 elements)")
    angles: HousesAngles = Field(..., description="Angles (Ascendant, MC)")


class DesignTimeResponse(BaseModel):
    """Response model for design time calculation."""

    birth_jd_ut: float = Field(..., description="Birth Julian Day in UT")
    design_jd_ut: float = Field(..., description="Design Julian Day in UT")
    target_sun_lon: float = Field(..., description="Target Sun longitude in degrees")
    achieved_sun_lon: float = Field(..., description="Achieved Sun longitude in degrees")
    delta_deg: float = Field(..., description="Difference in degrees")
    iterations: int = Field(..., description="Number of iterations")


class VersionResponse(BaseModel):
    """Response model for version endpoint."""

    service: str = Field(..., description="Service name")
    api_version: str = Field(..., description="API version")
    git_commit: str = Field(..., description="Git commit hash")
    build_tag: str = Field(..., description="Build tag/version")
    build_time_utc: str = Field(..., description="Build time in UTC")


class SourceResponse(BaseModel):
    """Response model for source endpoint."""

    license: str = Field(..., description="License type")
    repo: str = Field(..., description="Repository URL")
    tag: str = Field(..., description="Tag/version")
    commit: str = Field(..., description="Git commit hash")
    how_to_get_source: str = Field(..., description="Instructions to get source code")
