"""Geocoding tools for resolving location coordinates"""

from typing import Dict, Any, Optional
import logging
import httpx
import json

logger = logging.getLogger(__name__)


async def geocode_address(address: str) -> Dict[str, Any]:
    """
    Geocode an address using Nominatim (OpenStreetMap) API.
    This is a free, no-API-key-required geocoding service.
    
    **Rate Limiting**: Nominatim requires max 1 request per second.
    This function includes automatic rate limiting and retry logic.
    
    Args:
        address: Full address string (e.g., "Mumbai, Maharashtra, India")
    
    Returns:
        Dictionary containing location data with coordinates and timezone
    """
    import asyncio
    
    try:
        # Use Nominatim geocoding API (free, no API key required)
        # IMPORTANT: Nominatim requires max 1 request per second
        base_url = "https://nominatim.openstreetmap.org/search"
        
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        headers = {
            "User-Agent": "AstroGuru-AI/1.0 (Contact: support@example.com)",  # Required by Nominatim, should include contact
            "Accept": "application/json",
            "Accept-Language": "en"
        }
        
        # Rate limiting: Nominatim requires max 1 request per second
        # Add a small delay to respect rate limits
        await asyncio.sleep(1.0)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params=params, headers=headers)
            
            # Handle rate limiting
            if response.status_code == 429 or response.status_code == 509:
                logger.warning(f"Rate limited by Nominatim (status {response.status_code}), waiting 2 seconds and retrying...")
                await asyncio.sleep(2.0)
                # Retry once
                response = await client.get(base_url, params=params, headers=headers)
            
            response.raise_for_status()
            data = response.json()
        
        if not data or len(data) == 0:
            logger.warning(f"No results found for address: {address}")
            return {
                "success": False,
                "error": f"No location found for: {address}",
                "address": address
            }
        
        # Get the first (most relevant) result
        result = data[0]
        
        # Extract location details
        address_parts = result.get("address", {})
        
        location_data = {
            "success": True,
            "place_name": result.get("display_name", address),
            "city": (
                address_parts.get("city") or 
                address_parts.get("town") or 
                address_parts.get("village") or
                address_parts.get("municipality") or
                ""
            ),
            "state": (
                address_parts.get("state") or
                address_parts.get("region") or
                ""
            ),
            "country": address_parts.get("country", ""),
            "latitude": float(result.get("lat", 0)),
            "longitude": float(result.get("lon", 0)),
            "timezone": _get_timezone_from_coordinates(
                float(result.get("lat", 0)),
                float(result.get("lon", 0))
            )
        }
        
        logger.info(f"Geocoded '{address}' to {location_data['latitude']}, {location_data['longitude']}")
        return location_data
        
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code == 429 or status_code == 509:
            error_msg = f"Rate limit exceeded by geocoding service (Status: {status_code}). Please wait a moment and try again."
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "address": address,
                "retry_after": 2
            }
        else:
            logger.error(f"HTTP error geocoding address (Status: {status_code}): {e}")
            return {
                "success": False,
                "error": f"Geocoding service error (Status: {status_code}): {str(e)}",
                "address": address
            }
    except httpx.HTTPError as e:
        logger.error(f"HTTP error geocoding address: {e}")
        return {
            "success": False,
            "error": f"Geocoding service error: {str(e)}",
            "address": address
        }
    except Exception as e:
        logger.error(f"Error geocoding address: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Geocoding failed: {str(e)}",
            "address": address
        }


def _get_timezone_from_coordinates(latitude: float, longitude: float) -> str:
    """
    Get timezone from coordinates using timezonefinder library if available,
    otherwise fall back to simple lookup.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
    
    Returns:
        IANA timezone string (e.g., "Asia/Kolkata")
    """
    # Try to use timezonefinder library if available (more accurate)
    try:
        from timezonefinder import TimezoneFinder
        tf = TimezoneFinder()
        timezone = tf.timezone_at(lat=latitude, lng=longitude)
        if timezone:
            return timezone
    except ImportError:
        logger.debug("timezonefinder not available, using simple timezone lookup")
    except Exception as e:
        logger.warning(f"Error using timezonefinder: {e}, falling back to simple lookup")
    
    # Fallback: Simple timezone mapping for common regions
    # India and nearby regions
    if 6.0 <= latitude <= 37.0 and 68.0 <= longitude <= 97.0:
        return "Asia/Kolkata"
    
    # USA - Eastern
    if 24.0 <= latitude <= 50.0 and -85.0 <= longitude <= -66.0:
        return "America/New_York"
    
    # USA - Central
    if 24.0 <= latitude <= 50.0 and -102.0 <= longitude <= -85.0:
        return "America/Chicago"
    
    # USA - Mountain
    if 24.0 <= latitude <= 50.0 and -115.0 <= longitude <= -102.0:
        return "America/Denver"
    
    # USA - Pacific
    if 24.0 <= latitude <= 50.0 and -125.0 <= longitude <= -115.0:
        return "America/Los_Angeles"
    
    # UK
    if 49.0 <= latitude <= 61.0 and -8.0 <= longitude <= 2.0:
        return "Europe/London"
    
    # Europe - Central
    if 35.0 <= latitude <= 55.0 and 5.0 <= longitude <= 25.0:
        return "Europe/Berlin"
    
    # Australia - Sydney
    if -45.0 <= latitude <= -10.0 and 113.0 <= longitude <= 154.0:
        return "Australia/Sydney"
    
    # Default to UTC if unknown
    logger.warning(f"Unknown timezone for coordinates {latitude}, {longitude}, defaulting to UTC")
    return "UTC"


async def reverse_geocode(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Reverse geocode coordinates to get address details.
    
    **Rate Limiting**: Nominatim requires max 1 request per second.
    This function includes automatic rate limiting and retry logic.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
    
    Returns:
        Dictionary containing location data
    """
    import asyncio
    
    try:
        # Use Nominatim reverse geocoding API
        # IMPORTANT: Nominatim requires max 1 request per second
        base_url = "https://nominatim.openstreetmap.org/reverse"
        
        params = {
            "lat": str(latitude),
            "lon": str(longitude),
            "format": "json",
            "addressdetails": 1
        }
        
        headers = {
            "User-Agent": "AstroGuru-AI/1.0 (Contact: support@example.com)",  # Required by Nominatim
            "Accept": "application/json",
            "Accept-Language": "en"
        }
        
        # Rate limiting: Nominatim requires max 1 request per second
        await asyncio.sleep(1.0)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params=params, headers=headers)
            
            # Handle rate limiting
            if response.status_code == 429 or response.status_code == 509:
                logger.warning(f"Rate limited by Nominatim (status {response.status_code}), waiting 2 seconds and retrying...")
                await asyncio.sleep(2.0)
                # Retry once
                response = await client.get(base_url, params=params, headers=headers)
            
            response.raise_for_status()
            result = response.json()
        
        if not result:
            return {
                "success": False,
                "error": "No location found for coordinates",
                "latitude": latitude,
                "longitude": longitude
            }
        
        address_parts = result.get("address", {})
        
        location_data = {
            "success": True,
            "place_name": result.get("display_name", ""),
            "city": (
                address_parts.get("city") or 
                address_parts.get("town") or 
                address_parts.get("village") or
                address_parts.get("municipality") or
                ""
            ),
            "state": (
                address_parts.get("state") or
                address_parts.get("region") or
                ""
            ),
            "country": address_parts.get("country", ""),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": _get_timezone_from_coordinates(latitude, longitude)
        }
        
        return location_data
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429 or e.response.status_code == 509:
            error_msg = f"Rate limit exceeded by geocoding service. Please wait a moment and try again. (Status: {e.response.status_code})"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "latitude": latitude,
                "longitude": longitude,
                "retry_after": 2
            }
        else:
            logger.error(f"HTTP error reverse geocoding: {e}")
            return {
                "success": False,
                "error": f"Reverse geocoding service error: {str(e)}",
                "latitude": latitude,
                "longitude": longitude
            }
    except httpx.HTTPError as e:
        logger.error(f"HTTP error reverse geocoding: {e}")
        return {
            "success": False,
            "error": f"Reverse geocoding service error: {str(e)}",
            "latitude": latitude,
            "longitude": longitude
        }
    except Exception as e:
        logger.error(f"Error reverse geocoding: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Reverse geocoding failed: {str(e)}",
            "latitude": latitude,
            "longitude": longitude
        }

