"""Swiss Ephemeris wrapper for astronomical calculations."""

import os
from typing import Dict, List, Optional, Tuple
import swisseph as swe

# Swiss Ephemeris body constants
BODY_CODES: Dict[str, int] = {
    # Classical planets
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
    # Lunar nodes
    "TrueNode": swe.TRUE_NODE,  # True North Node (Rahu)
    "MeanNode": swe.MEAN_NODE,  # Mean North Node
    # Asteroids and minor bodies
    "Chiron": swe.CHIRON,  # Chiron (2060)
    "Ceres": swe.CERES,  # Ceres (1)
    "Pallas": swe.PALLAS,  # Pallas (2)
    "Juno": swe.JUNO,  # Juno (3)
    "Vesta": swe.VESTA,  # Vesta (4)
    # Lunar apogee/perigee (Lilith)
    "MeanLilith": swe.MEAN_APOG,  # Mean Black Moon Lilith
    "OscLilith": swe.OSCU_APOG,  # Oscillating (True) Black Moon Lilith
    "Lilith": swe.MEAN_APOG,  # Alias for Mean Lilith
    # White Moon (Selena) - calculated as opposite of Lilith
    # Note: Swiss Ephemeris doesn't have Selena directly, we compute it separately
}

# House system codes (Swiss Ephemeris uses single-byte ASCII codes)
# Reference: https://www.astro.com/swisseph/swephprg.htm#_Toc505244836
HOUSE_SYSTEMS: Dict[str, bytes] = {
    "P": b'P',  # Placidus
    "K": b'K',  # Koch
    "R": b'R',  # Regiomontanus
    "C": b'C',  # Campanus
    "E": b'E',  # Equal (cusp 1 = Asc)
    "V": b'V',  # Vehlow equal (Asc in middle of house 1)
    "W": b'W',  # Whole Sign
    "X": b'X',  # Axial Rotation / Meridian
    "H": b'H',  # Azimuthal / Horizontal
    "T": b'T',  # Topocentric (Polich/Page)
    "M": b'M',  # Morinus
    "B": b'B',  # Alcabitius
    "Y": b'Y',  # APC houses
    "O": b'O',  # Porphyrius
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


def get_house_system_code(house_system: str) -> bytes:
    """
    Get Swiss Ephemeris house system code from name.

    Args:
        house_system: House system code (e.g., "P" for Placidus)

    Returns:
        Swiss Ephemeris house system code as bytes

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

    # pyswisseph.calc_ut returns (xx, retflag) where:
    # xx = tuple of 6 floats: [lon, lat, dist, lon_speed, lat_speed, dist_speed]
    # retflag = return flags (negative on error)
    xx, retflag = swe.calc_ut(jd_ut, body_code, flags)

    if retflag < 0:
        raise RuntimeError(f"Swiss Ephemeris error {retflag} for {body_name}")

    longitude = xx[0]  # Ecliptic longitude
    speed = xx[3] if len(xx) > 3 else None  # Longitude speed

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
            # Special computed points
            if body_name == "Selena" or body_name == "WhiteMoon":
                # White Moon (Selena) = Lilith + 180°
                lilith_lon, _ = calculate_position(jd_ut, "MeanLilith", flags)
                longitude = (lilith_lon + 180.0) % 360.0
            elif body_name == "SouthNode":
                # South Node (Ketu) = North Node + 180°
                north_node_lon, _ = calculate_position(jd_ut, "TrueNode", flags)
                longitude = (north_node_lon + 180.0) % 360.0
            else:
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

    # Calculate houses using pyswisseph
    # swe.houses() returns (cusps_tuple, ascmc_tuple)
    # cusps_tuple: 12 house cusps (index 0-11 = houses 1-12)
    # ascmc_tuple: [0]=Asc, [1]=MC, [2]=ARMC, [3]=Vertex, [4]=equatorial Asc, etc.
    cusps, ascmc = swe.houses(jd_ut, lat, lon, house_system_code)

    # Convert to list and prepend 0 to match expected format (index = house number)
    cusps_list = [0.0] + list(cusps)

    angles = {
        "asc": ascmc[0],  # Ascendant
        "mc": ascmc[1],  # MC (Midheaven)
    }

    return cusps_list, angles


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
