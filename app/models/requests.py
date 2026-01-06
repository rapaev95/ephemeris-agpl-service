"""Pydantic models for API requests."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PositionsFlags(BaseModel):
    """Flags for positions calculation."""

    sidereal: bool = Field(default=False, description="Use sidereal zodiac")
    ayanamsa: Optional[int] = Field(default=None, description="Ayanamsa code for sidereal")
    include_speed: bool = Field(default=False, description="Include speed in results")


class PositionsRequest(BaseModel):
    """Request model for positions calculation."""

    jd_ut: float = Field(..., description="Julian Day in UT", ge=0)
    bodies: List[str] = Field(..., description="List of celestial bodies to calculate")
    flags: Optional[PositionsFlags] = Field(default=None, description="Calculation flags")
    include_speed: bool = Field(default=False, description="Include speed in results")


class HousesRequest(BaseModel):
    """Request model for houses calculation."""

    jd_ut: float = Field(..., description="Julian Day in UT", ge=0)
    lat: float = Field(..., description="Latitude in degrees", ge=-90, le=90)
    lon: float = Field(..., description="Longitude in degrees", ge=-180, le=180)
    house_system: str = Field(default="P", description="House system code (P=Placidus)")


class SearchWindowDays(BaseModel):
    """Search window for design time calculation."""

    min: int = Field(..., description="Minimum days before birth", ge=0)
    max: int = Field(..., description="Maximum days before birth", ge=0)


class DesignTimeRequest(BaseModel):
    """Request model for design time calculation."""

    birth_jd_ut: float = Field(..., description="Birth Julian Day in UT", ge=0)
    sun_offset_deg: float = Field(default=88.0, description="Solar arc offset in degrees")
    search_window_days: SearchWindowDays = Field(
        ..., description="Search window for design time"
    )
    tolerance_deg: float = Field(
        default=0.01, description="Tolerance for convergence in degrees", gt=0
    )
    max_iter: int = Field(default=80, description="Maximum iterations", gt=0)
