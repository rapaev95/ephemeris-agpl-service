"""Swiss Ephemeris wrapper for astronomical calculations."""

import os
from typing import Dict, List, Optional, Tuple
import swisseph as swe

# Swiss Ephemeris body constants
BODY_CODES: Dict[str, int] = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "TrueNode": swe.TRUE_NODE,  # True North Node
    "MeanNode": swe.MEAN_NODE,  # Mean North Node
}

# House system codes
HOUSE_SYSTEMS: Dict[str, int] = {
    "P": swe.PLACIDUS,  # Placidus
    "K": swe.KOCH,  # Koch
    "R": swe.REGIO,  # Regiomontanus
    "C": swe.CAMPANUS,  # Campanus
    "E": swe.EQUAL,  # Equal
    "V": swe.VEHLOW,  # Vehlow
    "W": swe.WHOLE_SIGN,  # Whole Sign
    "X": swe.AXIAL_ROTATION,  # Axial Rotation
    "H": swe.HORIZONTAL,  # Horizontal
    "T": swe.TOPOCENTRIC,  # Topocentric
    "M": swe.MORINUS,  # Morinus
    "B": swe.ALCABITUS,  # Alcabitius
    "Y": swe.PORPHYRIUS,  # Porphyrius
    "L": swe.ALCABITUS,  # Alcabitius (alias)
    "A": swe.ALCABITUS,  # Alcabitius (alias)
}

_ephe_path_initialized = False


def initialize_ephemeris_path() -> None:
    """
    Initialize Swiss Ephemeris data file path.

    Must be called before any calculations.
    """
    global _ephe_path_initialized
    if _ephe_path_initialized:
        return

    sweph_path = os.getenv("SWEPH_PATH", "./sweph")
    swe.set_ephe_path(sweph_path)
    _ephe_path_initialized = True


def get_body_code(body_name: str) -> int:
    """
    Get Swiss Ephemeris body code from name.

    Args:
        body_name: Name of celestial body (e.g., "Sun", "Moon")

    Returns:
        Swiss Ephemeris body code

    Raises:
        ValueError: If body name is not supported
    """
    if body_name not in BODY_CODES:
        raise ValueError(f"Unsupported body: {body_name}")

    return BODY_CODES[body_name]


def get_house_system_code(house_system: str) -> int:
    """
    Get Swiss Ephemeris house system code from name.

    Args:
        house_system: House system code (e.g., "P" for Placidus)

    Returns:
        Swiss Ephemeris house system code

    Raises:
        ValueError: If house system is not supported
    """
    if house_system not in HOUSE_SYSTEMS:
        raise ValueError(f"Unsupported house system: {house_system}")

    return HOUSE_SYSTEMS[house_system]


def calculate_position(
    jd_ut: float,
    body_name: str,
    flags: int = swe.FLG_SWIEPH | swe.FLG_SPEED,
) -> Tuple[float, Optional[float]]:
    """
    Calculate ecliptic longitude and speed of a celestial body.

    Args:
        jd_ut: Julian Day in UT
        body_name: Name of celestial body
        flags: Calculation flags (default includes speed)

    Returns:
        Tuple of (longitude in degrees, speed in degrees/day or None)
    """
    initialize_ephemeris_path()

    body_code = get_body_code(body_name)
    result = swe.calc_ut(jd_ut, body_code, flags)

    if result[0] < 0:
        raise RuntimeError(f"Swiss Ephemeris error {result[0]} for {body_name}")

    longitude = result[1][0]  # Ecliptic longitude
    speed = result[1][1] if len(result[1]) > 1 else None  # Speed

    return longitude, speed


def calculate_positions(
    jd_ut: float,
    bodies: List[str],
    include_speed: bool = False,
    sidereal: bool = False,
    ayanamsa: Optional[int] = None,
) -> Dict[str, float]:
    """
    Calculate positions for multiple celestial bodies.

    Args:
        jd_ut: Julian Day in UT
        bodies: List of body names
        include_speed: Whether to include speed in results
        sidereal: Whether to use sidereal zodiac
        ayanamsa: Ayanamsa code for sidereal calculations

    Returns:
        Dictionary mapping body names to longitudes (and optionally speeds)
    """
    flags = swe.FLG_SWIEPH
    if include_speed:
        flags |= swe.FLG_SPEED

    if sidereal:
        flags |= swe.FLG_SIDEREAL
        if ayanamsa is not None:
            swe.set_sid_mode(ayanamsa, 0, 0)

    positions: Dict[str, float] = {}

    for body_name in bodies:
        try:
            longitude, _ = calculate_position(jd_ut, body_name, flags)
            positions[body_name] = longitude
        except (ValueError, RuntimeError) as e:
            raise ValueError(f"Error calculating {body_name}: {str(e)}")

    return positions


def calculate_houses(
    jd_ut: float,
    lat: float,
    lon: float,
    house_system: str = "P",
) -> Tuple[List[float], Dict[str, float]]:
    """
    Calculate house cusps and angles (Ascendant, MC).

    Args:
        jd_ut: Julian Day in UT
        lat: Latitude in degrees
        lon: Longitude in degrees
        house_system: House system code (default: "P" for Placidus)

    Returns:
        Tuple of (cusps list with 13 elements, angles dict with "asc" and "mc")
    """
    initialize_ephemeris_path()

    house_system_code = get_house_system_code(house_system)

    # Calculate houses
    result = swe.houses(jd_ut, lat, lon, house_system_code)

    if result[0] < 0:
        raise RuntimeError(f"Swiss Ephemeris error {result[0]} for houses calculation")

    # result[1] contains cusps (13 elements: 0-12, where 0 is always 0)
    # result[2] contains ascmc (Ascendant, MC, etc.)
    cusps = list(result[1])
    ascmc = result[2]

    angles = {
        "asc": ascmc[0],  # Ascendant
        "mc": ascmc[1],  # MC (Midheaven)
    }

    return cusps, angles


def calculate_sun_position(jd_ut: float) -> float:
    """
    Calculate Sun's ecliptic longitude.

    Args:
        jd_ut: Julian Day in UT

    Returns:
        Sun's longitude in degrees
    """
    longitude, _ = calculate_position(jd_ut, "Sun")
    return longitude
