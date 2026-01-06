"""API routes for Human Design time calculation."""

from fastapi import APIRouter, Depends, Response
from app.core.auth import require_auth
from app.core.swe import calculate_sun_position
from app.core.angle import normalize_angle, angle_difference, angle_within_tolerance
from app.core.versioning import get_source_header
from app.core.errors import raise_no_convergence, raise_bad_request
from app.models.requests import DesignTimeRequest
from app.models.responses import DesignTimeResponse

router = APIRouter()


@router.post("/v1/design-time", response_model=DesignTimeResponse, tags=["calculations"])
async def calculate_design_time_endpoint(
    request: DesignTimeRequest,
    response: Response,
    _token: str = Depends(require_auth),
) -> DesignTimeResponse:
    """
    Find design_jd_ut for Human Design: moment before birth when Sun is at offset degrees earlier.

    Uses binary search to find the moment when Sun's longitude equals
    (birth_sun_lon - sun_offset_deg) mod 360.

    Args:
        request: Design time calculation request
        response: FastAPI response object (for headers)
        _token: Authentication token (from dependency)

    Returns:
        Design time with achieved accuracy

    Raises:
        HTTPException: If convergence fails or calculation error occurs
    """
    # Validate search window
    if request.search_window_days.min >= request.search_window_days.max:
        raise_bad_request(
            "search_window_days.min must be less than search_window_days.max"
        )

    # Get Sun position at birth
    try:
        birth_sun_lon = calculate_sun_position(request.birth_jd_ut)
        birth_sun_lon = normalize_angle(birth_sun_lon)
    except Exception as e:
        raise_bad_request(f"Error calculating birth Sun position: {str(e)}")

    # Calculate target longitude (offset degrees earlier)
    target_sun_lon = normalize_angle(birth_sun_lon - request.sun_offset_deg)

    # Search window in Julian Days
    search_start_jd = request.birth_jd_ut - request.search_window_days.max
    search_end_jd = request.birth_jd_ut - request.search_window_days.min

    # Binary search
    iterations = 0
    design_jd_ut = None
    achieved_sun_lon = None

    while iterations < request.max_iter:
        iterations += 1

        # Check if window is small enough
        window_size = search_end_jd - search_start_jd
        if window_size < 1e-6:  # Less than ~0.1 seconds
            design_jd_ut = (search_start_jd + search_end_jd) / 2.0
            try:
                achieved_sun_lon = calculate_sun_position(design_jd_ut)
                achieved_sun_lon = normalize_angle(achieved_sun_lon)
            except Exception as e:
                raise_bad_request(f"Error calculating design Sun position: {str(e)}")

            delta = abs(angle_difference(achieved_sun_lon, target_sun_lon))
            if angle_within_tolerance(achieved_sun_lon, target_sun_lon, request.tolerance_deg):
                break

        # Midpoint
        mid_jd = (search_start_jd + search_end_jd) / 2.0

        try:
            mid_sun_lon = calculate_sun_position(mid_jd)
            mid_sun_lon = normalize_angle(mid_sun_lon)
        except Exception as e:
            raise_bad_request(f"Error calculating mid Sun position: {str(e)}")

        # Calculate difference (handling wrap-around)
        diff = angle_difference(mid_sun_lon, target_sun_lon)

        # Check convergence
        if abs(diff) <= request.tolerance_deg:
            design_jd_ut = mid_jd
            achieved_sun_lon = mid_sun_lon
            break

        # Update search window
        if diff > 0:
            # Sun is ahead of target, need to go earlier
            search_end_jd = mid_jd
        else:
            # Sun is behind target, need to go later
            search_start_jd = mid_jd

    # Check if we found a solution
    if design_jd_ut is None or achieved_sun_lon is None:
        raise_no_convergence(
            f"Failed to find design time within {request.max_iter} iterations",
            details={
                "iterations": iterations,
                "tolerance_deg": request.tolerance_deg,
                "search_window_days": {
                    "min": request.search_window_days.min,
                    "max": request.search_window_days.max,
                },
            },
        )

    # Final check
    delta = abs(angle_difference(achieved_sun_lon, target_sun_lon))
    if delta > request.tolerance_deg:
        raise_no_convergence(
            f"Failed to achieve tolerance: delta={delta:.6f} > tolerance={request.tolerance_deg}",
            details={
                "iterations": iterations,
                "delta_deg": delta,
                "tolerance_deg": request.tolerance_deg,
            },
        )

    # Add X-AGPL-Source header
    response.headers["X-AGPL-Source"] = get_source_header()

    return DesignTimeResponse(
        birth_jd_ut=request.birth_jd_ut,
        design_jd_ut=design_jd_ut,
        target_sun_lon=target_sun_lon,
        achieved_sun_lon=achieved_sun_lon,
        delta_deg=delta,
        iterations=iterations,
    )
