"""jyotishganit tools for accurate Vedic astrology calculations.

This module provides wrapper functions for jyotishganit library,
making them available as tools for the agent system.

jyotishganit uses NASA JPL ephemeris data for high-precision calculations
and provides complete birth chart generation with all divisional charts.

**IMPORTANT**: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
This simplifies timezone handling and avoids confusion. All birth times should be
provided in IST format, regardless of the actual location of birth.
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, date, timedelta
import logging
import re

try:
    from jyotishganit import calculate_birth_chart
except ImportError:
    calculate_birth_chart = None

logger = logging.getLogger(__name__)

# Planet order in jyotishganit: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Nakshatra names in order
NAKSHATRAS = [
    "Ashwini", "Bharani", "Kritika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshta", "Moola", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

# Nakshatra lords mapping (repeats every 9 nakshatras)
NAKSHATRA_LORDS = {
    "Ashwini": "Ketu", "Bharani": "Venus", "Kritika": "Sun", "Rohini": "Moon",
    "Mrigashira": "Mars", "Ardra": "Rahu", "Punarvasu": "Jupiter", "Pushya": "Saturn",
    "Ashlesha": "Mercury", "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
    "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu", "Vishakha": "Jupiter",
    "Anuradha": "Saturn", "Jyeshta": "Mercury", "Moola": "Ketu", "Purva Ashadha": "Venus",
    "Uttara Ashadha": "Sun", "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
    "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury"
}

# Dasha periods in years
DASHA_PERIODS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

# Dasha sequence
DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]


def _parse_datetime(date_str: str, time_str: str) -> datetime:
    """Parse date and time strings into naive datetime object.
    
    All times are assumed to be in IST (Indian Standard Time).
    Returns a naive datetime object for jyotishganit compatibility.
    """
    # Combine date and time
    dt_str = f"{date_str} {time_str}"
    
    # Parse to datetime (naive - no timezone)
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except ValueError:
        # Try with seconds
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    # Return naive datetime (jyotishganit works with naive datetime + timezone_offset)
    return dt


def _get_timezone_offset() -> float:
    """Get IST (Indian Standard Time) timezone offset in hours from UTC.
    
    IST is UTC+5:30, so this always returns 5.5.
    """
    return 5.5  # IST offset is fixed at UTC+5:30


def _calculate_chart(
    date_of_birth: str,
    time_of_birth: str,
    latitude: float,
    longitude: float,
    location_name: str,
    name: Optional[str] = None
) -> Any:
    """Calculate birth chart using jyotishganit.
    
    All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    """
    if calculate_birth_chart is None:
        raise ImportError(
            "jyotishganit package not installed. Install with: pip install jyotishganit"
        )
    
    # Validate inputs
    if not date_of_birth or not time_of_birth:
        raise ValueError("date_of_birth and time_of_birth are required")
    
    if latitude is None or longitude is None:
        raise ValueError("latitude and longitude are required")
    
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        raise ValueError(f"latitude and longitude must be numbers, got latitude={type(latitude)}, longitude={type(longitude)}")
    
    if not (-90 <= latitude <= 90):
        raise ValueError(f"latitude must be between -90 and 90, got {latitude}")
    
    if not (-180 <= longitude <= 180):
        raise ValueError(f"longitude must be between -180 and 180, got {longitude}")
    
    # Parse datetime (returns naive datetime in IST)
    try:
        birth_datetime = _parse_datetime(date_of_birth, time_of_birth)
    except Exception as e:
        raise ValueError(f"Failed to parse date/time: {date_of_birth} {time_of_birth}. Error: {e}")
    
    # Get IST timezone offset (UTC+5:30 = 5.5 hours)
    timezone_offset = _get_timezone_offset()  # Always 5.5 for IST
    
    # Calculate chart
    # jyotishganit works with naive datetime + timezone_offset
    # birth_datetime is already naive (no timezone info)
    try:
        chart = calculate_birth_chart(
            birth_date=birth_datetime,  # Naive datetime (assumed to be in IST)
            latitude=latitude,
            longitude=longitude,
            timezone_offset=timezone_offset,  # 5.5 for IST
            name=name or "Person",
            location_name=location_name
        )
    except Exception as e:
        logger.error(f"Error calculating chart with jyotishganit: {e}", exc_info=True)
        raise ValueError(f"Chart calculation failed: {e}")
    
    return chart


async def address_to_geolocation(address: str) -> Dict[str, Any]:
    """
    Note: jyotishganit does not provide address geocoding.
    This function is kept for compatibility but requires external geocoding service.
    
    Args:
        address: Full address string (e.g., "Mumbai, Maharashtra, India")
    
    Returns:
        Dictionary indicating that external geocoding is needed
    """
    logger.warning("address_to_geolocation requires external geocoding service. jyotishganit does not provide this.")
    return {
        "success": False,
        "error": "jyotishganit does not provide address geocoding. Use an external geocoding service.",
        "address": address,
        "note": "Consider using Google Geocoding API, Nominatim, or similar service"
    }


async def coordinates_to_geolocation(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Note: jyotishganit does not provide reverse geocoding.
    This function is kept for compatibility but requires external service.
    
    Args:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
    
    Returns:
        Dictionary indicating that external reverse geocoding is needed
    """
    logger.warning("coordinates_to_geolocation requires external reverse geocoding service.")
    return {
        "success": False,
        "error": "jyotishganit does not provide reverse geocoding. Use an external service.",
        "latitude": latitude,
        "longitude": longitude,
        "note": "Consider using Google Geocoding API, Nominatim, or similar service"
    }


async def get_planetary_positions(
    date_of_birth: str,
    time_of_birth: str,
    latitude: float,
    longitude: float,
    location_name: str,
    chart: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get detailed planetary positions for a given birth time and location.
    
    Note: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    
    Args:
        date_of_birth: Date in YYYY-MM-DD format
        time_of_birth: Time in HH:MM format (24-hour) - assumed to be in IST
        latitude: Birth location latitude
        longitude: Birth location longitude
        location_name: Full location name
        chart: Optional pre-calculated chart object (for optimization)
    
    Returns:
        Dictionary containing planetary positions for all planets
    """
    try:
        # Use provided chart or calculate new one (always uses IST)
        if chart is None:
            chart = _calculate_chart(date_of_birth, time_of_birth, latitude, longitude, location_name)
        
        # Extract planetary positions
        planets = {}
        for i, planet in enumerate(chart.d1_chart.planets):
            planet_name = PLANET_NAMES[i] if i < len(PLANET_NAMES) else f"Planet_{i}"
            
            planets[planet_name] = {
                "celestial_body": planet.celestial_body,
                "sign": planet.sign,
                "sign_degrees": planet.sign_degrees,
                "nakshatra": planet.nakshatra,
                "pada": planet.pada,
                "house": planet.house,
                "longitude": planet.sign_degrees,  # Degrees within sign
            }
            
            # Add dignities if available
            if hasattr(planet, 'dignities'):
                planets[planet_name]["dignities"] = {
                    "dignity": planet.dignities.dignity if hasattr(planet.dignities, 'dignity') else None,
                    "planet_tattva": planet.dignities.planet_tattva if hasattr(planet.dignities, 'planet_tattva') else None,
                }
        
        return {
            "success": True,
            "planetary_positions": planets,
            "birth_time": f"{date_of_birth} {time_of_birth}",
            "location": location_name,
            "ayanamsa": chart.ayanamsa if hasattr(chart, 'ayanamsa') else None
        }
    except Exception as e:
        logger.error(f"Error getting planetary positions: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_house_positions(
    date_of_birth: str,
    time_of_birth: str,
    latitude: float,
    longitude: float,
    location_name: str,
    chart: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get house positions and cusps for a given birth time and location.
    
    Note: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    
    Args:
        date_of_birth: Date in YYYY-MM-DD format
        time_of_birth: Time in HH:MM format (24-hour) - assumed to be in IST
        latitude: Birth location latitude
        longitude: Birth location longitude
        location_name: Full location name
        chart: Optional pre-calculated chart object (for optimization)
    
    Returns:
        Dictionary containing house cusps and positions
    """
    try:
        # Use provided chart or calculate new one (always uses IST)
        if chart is None:
            chart = _calculate_chart(date_of_birth, time_of_birth, latitude, longitude, location_name)
        
        # Get Lagna (Ascendant) - first house
        lagna_house = chart.d1_chart.houses[0]
        
        # Get all house cusps
        house_cusps = []
        house_details = []
        
        for i, house in enumerate(chart.d1_chart.houses):
            house_num = i + 1
            occupants = [p.celestial_body for p in house.occupants] if hasattr(house, 'occupants') else []
            
            house_cusps.append({
                "house": house_num,
                "sign": house.sign,
                "longitude": getattr(house, 'longitude', None)
            })
            
            house_details.append({
                "house": house_num,
                "sign": house.sign,
                "occupants": occupants
            })
        
        return {
            "success": True,
            "lagna": {
                "sign": lagna_house.sign,
                "house": 1,
                "longitude": getattr(lagna_house, 'longitude', None)
            },
            "house_cusps": house_cusps,
            "house_details": house_details,
            "birth_time": f"{date_of_birth} {time_of_birth}",
            "location": location_name
        }
    except Exception as e:
        logger.error(f"Error getting house positions: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_lagna_details(
    date_of_birth: str,
    time_of_birth: str,
    latitude: float,
    longitude: float,
    location_name: str,
    chart: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get detailed Lagna (Ascendant) information.
    
    Note: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    
    Args:
        date_of_birth: Date in YYYY-MM-DD format
        time_of_birth: Time in HH:MM format (24-hour) - assumed to be in IST
        latitude: Birth location latitude
        longitude: Birth location longitude
        location_name: Full location name
        chart: Optional pre-calculated chart object (for optimization)
    
    Returns:
        Dictionary containing Lagna details including sign, degree, nakshatra, etc.
    """
    try:
        # Use provided chart or calculate new one (always uses IST)
        if chart is None:
            chart = _calculate_chart(date_of_birth, time_of_birth, latitude, longitude, location_name)
        
        # Get Lagna (first house)
        lagna_house = chart.d1_chart.houses[0]
        
        # Get Lagna lord (sign lord)
        lagna_lord = None
        sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        lagna_lord = sign_lords.get(lagna_house.sign)
        
        return {
            "success": True,
            "lagna": {
                "sign": lagna_house.sign,
                "longitude": getattr(lagna_house, 'longitude', None),
                "lord": lagna_lord,
                "house": 1
            },
            "birth_time": f"{date_of_birth} {time_of_birth}",
            "location": location_name,
            "ayanamsa": chart.ayanamsa if hasattr(chart, 'ayanamsa') else None
        }
    except Exception as e:
        logger.error(f"Error getting Lagna details: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_dasha_details(
    date_of_birth: str,
    time_of_birth: str,
    latitude: float,
    longitude: float,
    location_name: str,
    years_ahead: int = 10,
    chart: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get Dasha (planetary period) details for a given birth time.
    
    Note: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    
    Args:
        date_of_birth: Date in YYYY-MM-DD format
        time_of_birth: Time in HH:MM format (24-hour) - assumed to be in IST
        latitude: Birth location latitude
        longitude: Birth location longitude
        location_name: Full location name
        years_ahead: Number of years to calculate ahead (default: 10)
        chart: Optional pre-calculated chart object (for optimization)
    
    Returns:
        Dictionary containing current and upcoming Dasha periods
    """
    try:
        # Use provided chart or calculate new one (always uses IST)
        if chart is None:
            chart = _calculate_chart(date_of_birth, time_of_birth, latitude, longitude, location_name)
        
        # Get Dasha information
        dashas = chart.dashas
        
        # Extract current and upcoming mahadashas
        current_dasha = None
        upcoming_dashas = []
        
        if hasattr(dashas, 'upcoming') and 'mahadashas' in dashas.upcoming:
            mahadashas = dashas.upcoming['mahadashas']
            
            # First one is current
            if mahadashas:
                first_key = list(mahadashas.keys())[0]
                first_dasha = mahadashas[first_key]
                current_dasha = {
                    "planet": first_key,
                    "start": first_dasha.get('start'),
                    "end": first_dasha.get('end'),
                    "duration_years": first_dasha.get('duration_years')
                }
                
                # Get upcoming dashas (limit by years_ahead)
                for planet, dasha_info in list(mahadashas.items())[1:]:
                    upcoming_dashas.append({
                        "planet": planet,
                        "start": dasha_info.get('start'),
                        "end": dasha_info.get('end'),
                        "duration_years": dasha_info.get('duration_years')
                    })
        
        return {
            "success": True,
            "current_dasha": current_dasha,
            "upcoming_dashas": upcoming_dashas[:years_ahead] if years_ahead else upcoming_dashas,
            "years_ahead": years_ahead,
            "birth_time": f"{date_of_birth} {time_of_birth}",
            "location": location_name
        }
    except Exception as e:
        logger.error(f"Error getting Dasha details: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_events_at_time(
    birth_date: str,
    birth_time: str,
    check_date: str,
    check_time: str,
    latitude: float,
    longitude: float,
    location_name: str,
    event_tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Note: jyotishganit does not provide event calculations at specific times.
    This would require calculating transits and aspects manually.
    
    Note: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    
    Args:
        birth_date: Birth date in YYYY-MM-DD format
        birth_time: Birth time in HH:MM format (assumed to be in IST)
        check_date: Date to check events for in YYYY-MM-DD format
        check_time: Time to check events for in HH:MM format (assumed to be in IST)
        latitude: Location latitude
        longitude: Location longitude
        location_name: Full location name
        event_tags: Optional list of event tags to filter
    
    Returns:
        Dictionary indicating that manual calculation is needed
    """
    logger.warning("get_events_at_time requires manual transit calculations with jyotishganit.")
    return {
        "success": False,
        "error": "jyotishganit does not provide event calculations. Calculate transits manually by comparing birth chart with current chart.",
        "check_time": f"{check_date} {check_time}",
        "birth_time": f"{birth_date} {birth_time}",
        "location": location_name,
        "note": "Calculate a new chart for check_time and compare planetary positions with birth chart"
    }


async def get_chart_summary(
    date_of_birth: str,
    time_of_birth: str,
    latitude: float,
    longitude: float,
    location_name: str,
    chart: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get a comprehensive chart summary including all key astrological data.
    
    Note: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    
    Args:
        date_of_birth: Date in YYYY-MM-DD format
        time_of_birth: Time in HH:MM format (24-hour) - assumed to be in IST
        latitude: Birth location latitude
        longitude: Birth location longitude
        location_name: Full location name
        chart: Optional pre-calculated chart object (for optimization)
    
    Returns:
        Dictionary containing comprehensive chart summary
    """
    try:
        # Use provided chart or calculate new one (always uses IST)
        if chart is None:
            chart = _calculate_chart(date_of_birth, time_of_birth, latitude, longitude, location_name)
        
        # Get Lagna
        lagna_house = chart.d1_chart.houses[0]
        sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        
        # Get Moon (Rashi)
        moon = chart.d1_chart.planets[1]  # Moon is index 1
        
        # Get Panchanga
        panchanga = chart.panchanga if hasattr(chart, 'panchanga') else None
        
        # Get planetary positions summary
        planets_summary = {}
        for i, planet in enumerate(chart.d1_chart.planets):
            planet_name = PLANET_NAMES[i] if i < len(PLANET_NAMES) else f"Planet_{i}"
            planets_summary[planet_name] = {
                "sign": planet.sign,
                "house": planet.house,
                "nakshatra": planet.nakshatra,
                "pada": planet.pada
            }
        
        # Get house summary
        houses_summary = []
        for i, house in enumerate(chart.d1_chart.houses):
            occupants = [p.celestial_body for p in house.occupants] if hasattr(house, 'occupants') else []
            houses_summary.append({
                "house": i + 1,
                "sign": house.sign,
                "occupants": occupants
            })
        
        return {
            "success": True,
            "lagna": {
                "sign": lagna_house.sign,
                "lord": sign_lords.get(lagna_house.sign)
            },
            "rashi": {
                "sign": moon.sign,
                "nakshatra": moon.nakshatra,
                "pada": moon.pada
            },
            "panchanga": {
                "tithi": panchanga.tithi if panchanga and hasattr(panchanga, 'tithi') else None,
                "nakshatra": panchanga.nakshatra if panchanga and hasattr(panchanga, 'nakshatra') else None,
                "yoga": panchanga.yoga if panchanga and hasattr(panchanga, 'yoga') else None,
                "karana": panchanga.karana if panchanga and hasattr(panchanga, 'karana') else None,
                "vaara": panchanga.vaara if panchanga and hasattr(panchanga, 'vaara') else None,
            },
            "planetary_positions": planets_summary,
            "house_positions": houses_summary,
            "ayanamsa": chart.ayanamsa if hasattr(chart, 'ayanamsa') else None,
            "birth_time": f"{date_of_birth} {time_of_birth}",
            "location": location_name
        }
    except Exception as e:
        logger.error(f"Error getting chart summary: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_shadbala_details(
    date_of_birth: str,
    time_of_birth: str,
    latitude: float,
    longitude: float,
    location_name: str,
    chart: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get Shadbala (six-fold strength) details for all planets.
    
    Note: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    
    Args:
        date_of_birth: Date in YYYY-MM-DD format
        time_of_birth: Time in HH:MM format (24-hour) - assumed to be in IST
        latitude: Birth location latitude
        longitude: Birth location longitude
        location_name: Full location name
        chart: Optional pre-calculated chart object (for optimization)
    
    Returns:
        Dictionary containing Shadbala calculations for all planets
    """
    try:
        # Use provided chart or calculate new one (always uses IST)
        if chart is None:
            chart = _calculate_chart(date_of_birth, time_of_birth, latitude, longitude, location_name)
        
        # Extract Shadbala for all planets
        shadbala_data = {}
        for i, planet in enumerate(chart.d1_chart.planets):
            planet_name = PLANET_NAMES[i] if i < len(PLANET_NAMES) else f"Planet_{i}"
            
            if hasattr(planet, 'shadbala') and planet.shadbala:
                shadbala = planet.shadbala.get('Shadbala', {}) if isinstance(planet.shadbala, dict) else {}
                
                shadbala_data[planet_name] = {
                    "total": shadbala.get('Total', 0),
                    "rupas": shadbala.get('Rupas', 0),
                    "sthanabala": shadbala.get('Sthanabala', 0),  # Positional strength
                    "kaalabala": shadbala.get('Kaalabala', 0),    # Temporal strength
                    "digbala": shadbala.get('Digbala', 0),        # Directional strength
                    "cheshtabala": shadbala.get('Cheshtabala', 0), # Motional strength
                    "naisargikabala": shadbala.get('Naisargikabala', 0), # Natural strength
                    "drikbala": shadbala.get('Drikbala', 0)       # Aspectual strength
                }
            else:
                shadbala_data[planet_name] = {
                    "error": "Shadbala data not available"
                }
        
        return {
            "success": True,
            "shadbala": shadbala_data,
            "birth_time": f"{date_of_birth} {time_of_birth}",
            "location": location_name
        }
    except Exception as e:
        logger.error(f"Error getting Shadbala details: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_divisional_charts(
    date_of_birth: str,
    time_of_birth: str,
    latitude: float,
    longitude: float,
    location_name: str,
    chart_types: Optional[List[str]] = None,
    chart: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get specific divisional charts (D1-D60) based on chart types.
    
    Note: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    
    Args:
        date_of_birth: Date in YYYY-MM-DD format
        time_of_birth: Time in HH:MM format (24-hour) - assumed to be in IST
        latitude: Birth location latitude
        longitude: Birth location longitude
        location_name: Full location name
        chart_types: List of chart types to retrieve (e.g., ['d1', 'd9', 'd10'])
                     If None, returns all available divisional charts
        chart: Optional pre-calculated chart object (for optimization)
    
    Returns:
        Dictionary containing requested divisional charts with planetary positions
    """
    try:
        # Use provided chart or calculate new one (always uses IST)
        if chart is None:
            chart = _calculate_chart(date_of_birth, time_of_birth, latitude, longitude, location_name)
        
        # Available divisional charts in jyotishganit
        available_charts = {
            'd1': 'Rasi', 'd2': 'Hora', 'd3': 'Drekkana', 'd4': 'Chaturthamsa',
            'd7': 'Saptamsa', 'd9': 'Navamsa', 'd10': 'Dasamsa', 'd12': 'Dwadasamsa',
            'd16': 'Shodasamsa', 'd24': 'Chaturvimsamsa', 'd27': 'Bhamsha',
            'd30': 'Trimsamsa', 'd60': 'Shashtiamsa'
        }
        
        # If no chart types specified, get all available
        if chart_types is None:
            chart_types = list(available_charts.keys())
        
        divisional_charts = {}
        
        for chart_type in chart_types:
            chart_key = chart_type.lower()
            if chart_key not in available_charts:
                logger.warning(f"Unknown chart type: {chart_type}, skipping")
                continue
            
            try:
                # Get divisional chart from chart.divisional_charts
                if hasattr(chart, 'divisional_charts') and chart.divisional_charts:
                    divisional_chart = chart.divisional_charts.get(chart_key)
                    
                    if divisional_chart:
                        # Extract planetary positions from divisional chart houses
                        # Planets are stored in house occupants, not as a direct .planets attribute
                        planets_data = {}
                        
                        # Iterate through all houses to collect planets from occupants
                        for house in divisional_chart.houses:
                            if hasattr(house, 'occupants') and house.occupants:
                                for planet_pos in house.occupants:
                                    if hasattr(planet_pos, 'celestial_body'):
                                        planet_name = planet_pos.celestial_body
                            planets_data[planet_name] = {
                                            "celestial_body": planet_pos.celestial_body,
                                            "sign": planet_pos.sign if hasattr(planet_pos, 'sign') else None,
                                            "house": house.number if hasattr(house, 'number') else None,
                                            "d1_house_placement": planet_pos.d1_house_placement if hasattr(planet_pos, 'd1_house_placement') else None
                            }
                        
                        # Extract house data
                        houses_data = []
                        for house in divisional_chart.houses:
                            occupants = []
                            if hasattr(house, 'occupants') and house.occupants:
                                occupants = [p.celestial_body for p in house.occupants if hasattr(p, 'celestial_body')]
                            houses_data.append({
                                "house": house.number if hasattr(house, 'number') else None,
                                "sign": house.sign if hasattr(house, 'sign') else None,
                                "lord": house.lord if hasattr(house, 'lord') else None,
                                "occupants": occupants,
                                "d1_house_placement": house.d1_house_placement if hasattr(house, 'd1_house_placement') else None
                            })
                        
                        # Extract ascendant information
                        ascendant_data = None
                        if hasattr(divisional_chart, 'ascendant') and divisional_chart.ascendant:
                            asc = divisional_chart.ascendant
                            ascendant_data = {
                                "sign": asc.sign if hasattr(asc, 'sign') else None,
                                "d1_house_placement": asc.d1_house_placement if hasattr(asc, 'd1_house_placement') else None
                            }
                        
                        divisional_charts[chart_key] = {
                            "name": available_charts[chart_key],
                            "ascendant": ascendant_data,
                            "planets": planets_data,
                            "houses": houses_data
                        }
                    else:
                        divisional_charts[chart_key] = {
                            "error": f"Chart {chart_key} not available"
                        }
                else:
                    divisional_charts[chart_key] = {
                        "error": "Divisional charts not available in chart object"
                    }
            except Exception as e:
                logger.warning(f"Error extracting {chart_key}: {e}")
                divisional_charts[chart_key] = {
                    "error": str(e)
                }
        
        return {
            "success": True,
            "divisional_charts": divisional_charts,
            "birth_time": f"{date_of_birth} {time_of_birth}",
            "location": location_name
        }
    except Exception as e:
        logger.error(f"Error getting divisional charts: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_comprehensive_chart(
    date_of_birth: str,
    time_of_birth: str,
    latitude: float,
    longitude: float,
    location_name: str,
    years_ahead: int = 10,
    divisional_charts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get comprehensive chart data including Lagna, Dasha, Shadbala, and Divisional Charts.
    This is the main tool that combines all chart calculations.
    
    Note: All times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
    
    Args:
        date_of_birth: Date in YYYY-MM-DD format
        time_of_birth: Time in HH:MM format (24-hour) - assumed to be in IST
        latitude: Birth location latitude
        longitude: Birth location longitude
        location_name: Full location name
        years_ahead: Number of years for Dasha calculations (default: 10)
        divisional_charts: List of divisional charts to include (e.g., ['d9', 'd10'])
                          If None, includes commonly used charts: ['d1', 'd2', 'd3', 'd4', 'd7', 'd9', 'd10', 'd12']
    
    Returns:
        Dictionary containing comprehensive chart data with all components
    """
    try:
        # OPTIMIZATION: Calculate chart once and reuse it for all operations
        logger.info("Calculating birth chart (optimized - single calculation, using IST)")
        chart = _calculate_chart(date_of_birth, time_of_birth, latitude, longitude, location_name)
        
        # Get all components using the same chart object - check each for success
        planetary_data = await get_planetary_positions(date_of_birth, time_of_birth, latitude, longitude, location_name, chart=chart)
        if not planetary_data.get("success", False):
            error_msg = planetary_data.get("error", "Unknown error getting planetary positions")
            logger.error(f"Failed to get planetary positions: {error_msg}")
            return {
                "success": False,
                "error": f"Failed to get planetary positions: {error_msg}"
            }
        
        lagna_data = await get_lagna_details(date_of_birth, time_of_birth, latitude, longitude, location_name, chart=chart)
        if not lagna_data.get("success", False):
            error_msg = lagna_data.get("error", "Unknown error getting lagna details")
            logger.error(f"Failed to get lagna details: {error_msg}")
            return {
                "success": False,
                "error": f"Failed to get lagna details: {error_msg}"
            }
        
        house_data = await get_house_positions(date_of_birth, time_of_birth, latitude, longitude, location_name, chart=chart)
        if not house_data.get("success", False):
            error_msg = house_data.get("error", "Unknown error getting house positions")
            logger.error(f"Failed to get house positions: {error_msg}")
            return {
                "success": False,
                "error": f"Failed to get house positions: {error_msg}"
            }
        
        # Optional components - continue even if they fail
        dasha_data = await get_dasha_details(date_of_birth, time_of_birth, latitude, longitude, location_name, years_ahead, chart=chart)
        shadbala_data = await get_shadbala_details(date_of_birth, time_of_birth, latitude, longitude, location_name, chart=chart)
        
        # Default divisional charts if not specified
        if divisional_charts is None:
            divisional_charts = ['d1', 'd2', 'd3', 'd4', 'd7', 'd9', 'd10', 'd12']
        
        divisional_data = await get_divisional_charts(date_of_birth, time_of_birth, latitude, longitude, location_name, divisional_charts, chart=chart)
        
        # Get chart summary for Panchanga
        chart_summary = await get_chart_summary(date_of_birth, time_of_birth, latitude, longitude, location_name, chart=chart)
        
        return {
            "success": True,
            "lagna": lagna_data.get("lagna", {}),
            "dasha": {
                "current_dasha": dasha_data.get("current_dasha") if dasha_data.get("success") else None,
                "upcoming_dashas": dasha_data.get("upcoming_dashas", []) if dasha_data.get("success") else []
            },
            "shadbala": shadbala_data.get("shadbala", {}) if shadbala_data.get("success") else {},
            "planetary_positions": planetary_data.get("planetary_positions", {}),
            "house_positions": house_data.get("house_details", []),
            "divisional_charts": divisional_data.get("divisional_charts", {}) if divisional_data.get("success") else {},
            "panchanga": chart_summary.get("panchanga", {}) if chart_summary.get("success") else {},
            "rashi": chart_summary.get("rashi", {}) if chart_summary.get("success") else {},
            "ayanamsa": chart_summary.get("ayanamsa"),
            "birth_time": f"{date_of_birth} {time_of_birth}",
            "location": location_name
        }
    except Exception as e:
        logger.error(f"Error getting comprehensive chart: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_today_date() -> Dict[str, Any]:
    """
    Get today's date in a standardized format.
    This tool provides the current date to agents for determining current vs upcoming periods.
    
    Call this tool with no arguments to get today's date.
    
    Returns:
        Dictionary containing today's date in YYYY-MM-DD format and additional date information:
        - success: bool - Whether the operation succeeded
        - today_date: str - Date in YYYY-MM-DD format (e.g., "2024-12-15")
        - year: int - Current year
        - month: int - Current month (1-12)
        - day: int - Current day (1-31)
        - day_of_week: str - Day name (e.g., "Monday")
        - iso_format: str - ISO format date string
    """
    try:
        today = date.today()
        result = {
            "success": True,
            "today_date": today.strftime("%Y-%m-%d"),
            "year": today.year,
            "month": today.month,
            "day": today.day,
            "day_of_week": today.strftime("%A"),
            "iso_format": today.isoformat()
        }
        logger.info(f"get_today_date tool called successfully, returning: {result['today_date']}")
        return result
    except Exception as e:
        logger.error(f"Error getting today's date: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "today_date": None
        }
