"""API routes for planet positions calculation."""

from fastapi import APIRouter, Depends, Response
from app.core.auth import require_auth
from app.core.swe import calculate_positions
from app.core.angle import normalize_angle
from app.core.versioning import get_source_header
from app.core.errors import raise_bad_request, ErrorCode
from app.models.requests import PositionsRequest
from app.models.responses import PositionsResponse, PositionsMeta

router = APIRouter()


@router.post("/v1/positions", response_model=PositionsResponse, tags=["calculations"])
async def calculate_positions_endpoint(
    request: PositionsRequest,
    response: Response,
    _token: str = Depends(require_auth),
) -> PositionsResponse:
    """
    Calculate ecliptic longitudes for celestial bodies.

    Args:
        request: Positions calculation request
        response: FastAPI response object (for headers)
        _token: Authentication token (from dependency)

    Returns:
        Positions of requested bodies in degrees (0-360)

    Raises:
        HTTPException: If body is unsupported or calculation fails
    """
    # Extract flags
    flags = request.flags
    sidereal = flags.sidereal if flags else False
    ayanamsa = flags.ayanamsa if flags else None
    include_speed = flags.include_speed if flags else request.include_speed

    try:
        # Calculate positions
        positions_raw = calculate_positions(
            jd_ut=request.jd_ut,
            bodies=request.bodies,
            include_speed=include_speed,
            sidereal=sidereal,
            ayanamsa=ayanamsa,
        )

        # Normalize all angles to [0, 360)
        positions = {body: normalize_angle(lon) for body, lon in positions_raw.items()}

        # Add X-AGPL-Source header
        response.headers["X-AGPL-Source"] = get_source_header()

        return PositionsResponse(
            jd_ut=request.jd_ut,
            positions=positions,
            meta=PositionsMeta(engine="swisseph", sidereal=sidereal),
        )

    except ValueError as e:
        error_msg = str(e)
        if "Unsupported body" in error_msg:
            raise_bad_request(
                error_msg,
                details={"code": ErrorCode.UNSUPPORTED_BODY, "bodies": request.bodies},
            )
        raise_bad_request(error_msg)
    except Exception as e:
        raise_bad_request(f"Calculation error: {str(e)}")
