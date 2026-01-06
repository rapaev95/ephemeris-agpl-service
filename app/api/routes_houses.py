"""API routes for houses calculation."""

from fastapi import APIRouter, Depends, Response
from app.core.auth import require_auth
from app.core.swe import calculate_houses
from app.core.angle import normalize_angle
from app.core.versioning import get_source_header
from app.core.errors import raise_bad_request, ErrorCode
from app.models.requests import HousesRequest
from app.models.responses import HousesResponse, HousesAngles

router = APIRouter()


@router.post("/v1/houses", response_model=HousesResponse, tags=["calculations"])
async def calculate_houses_endpoint(
    request: HousesRequest,
    response: Response,
    _token: str = Depends(require_auth),
) -> HousesResponse:
    """
    Calculate house cusps and angles (Ascendant, MC).

    Args:
        request: Houses calculation request
        response: FastAPI response object (for headers)
        _token: Authentication token (from dependency)

    Returns:
        House cusps and angles

    Raises:
        HTTPException: If house system is unsupported or calculation fails
    """
    try:
        # Calculate houses
        cusps_raw, angles_raw = calculate_houses(
            jd_ut=request.jd_ut,
            lat=request.lat,
            lon=request.lon,
            house_system=request.house_system,
        )

        # Normalize cusps and angles to [0, 360)
        cusps = [normalize_angle(cusp) for cusp in cusps_raw]
        angles = HousesAngles(
            asc=normalize_angle(angles_raw["asc"]),
            mc=normalize_angle(angles_raw["mc"]),
        )

        # Add X-AGPL-Source header
        response.headers["X-AGPL-Source"] = get_source_header()

        return HousesResponse(
            jd_ut=request.jd_ut,
            house_system=request.house_system,
            cusps=cusps,
            angles=angles,
        )

    except ValueError as e:
        error_msg = str(e)
        if "Unsupported house system" in error_msg:
            raise_bad_request(
                error_msg,
                details={
                    "code": ErrorCode.INVALID_HOUSE_SYSTEM,
                    "house_system": request.house_system,
                },
            )
        raise_bad_request(error_msg)
    except Exception as e:
        raise_bad_request(f"Calculation error: {str(e)}")
