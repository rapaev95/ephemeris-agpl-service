"""Error response models and HTTP exception handlers."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class ErrorCode:
    """Error codes for API responses."""

    BAD_REQUEST = "bad_request"
    UNAUTHORIZED = "unauthorized"
    NO_CONVERGENCE = "no_convergence"
    INTERNAL_ERROR = "internal_error"
    INVALID_BODY = "invalid_body"
    UNSUPPORTED_BODY = "unsupported_body"
    INVALID_HOUSE_SYSTEM = "invalid_house_system"


def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    """
    Create standardized error response.

    Args:
        code: Error code
        message: Human-readable error message
        details: Optional additional details
        status_code: HTTP status code

    Returns:
        JSONResponse with error format
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


def raise_bad_request(message: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Raise HTTP 400 Bad Request exception."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error": {
                "code": ErrorCode.BAD_REQUEST,
                "message": message,
                "details": details or {},
            }
        },
    )


def raise_unauthorized(message: str = "Invalid or missing authorization token") -> None:
    """Raise HTTP 401 Unauthorized exception."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": ErrorCode.UNAUTHORIZED,
                "message": message,
                "details": {},
            }
        },
    )


def raise_no_convergence(
    message: str = "Failed to find design time within tolerance",
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Raise HTTP 422 Unprocessable Entity for convergence failures."""
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "error": {
                "code": ErrorCode.NO_CONVERGENCE,
                "message": message,
                "details": details or {},
            }
        },
    )


def raise_internal_error(
    message: str = "Internal server error",
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Raise HTTP 500 Internal Server Error exception."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": message,
                "details": details or {},
            }
        },
    )
