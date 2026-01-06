"""Angle normalization and conversion utilities."""

from typing import Tuple


def normalize_angle(angle: float) -> float:
    """
    Normalize angle to range [0, 360).

    Args:
        angle: Angle in degrees (can be any value)

    Returns:
        Normalized angle in range [0, 360)
    """
    normalized = angle % 360.0
    if normalized < 0:
        normalized += 360.0
    return normalized


def angle_difference(angle1: float, angle2: float) -> float:
    """
    Calculate shortest angular difference between two angles.

    Args:
        angle1: First angle in degrees
        angle2: Second angle in degrees

    Returns:
        Difference in degrees, normalized to [-180, 180]
    """
    diff = normalize_angle(angle1) - normalize_angle(angle2)
    if diff > 180.0:
        diff -= 360.0
    elif diff < -180.0:
        diff += 360.0
    return diff


def angle_within_tolerance(angle1: float, angle2: float, tolerance: float) -> bool:
    """
    Check if two angles are within tolerance.

    Args:
        angle1: First angle in degrees
        angle2: Second angle in degrees
        tolerance: Tolerance in degrees

    Returns:
        True if angles are within tolerance
    """
    diff = abs(angle_difference(angle1, angle2))
    return diff <= tolerance


def degrees_to_dms(degrees: float) -> Tuple[int, int, float]:
    """
    Convert degrees to degrees, minutes, seconds.

    Args:
        degrees: Angle in decimal degrees

    Returns:
        Tuple of (degrees, minutes, seconds)
    """
    deg = int(degrees)
    minutes_float = (degrees - deg) * 60.0
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60.0
    return (deg, minutes, seconds)
