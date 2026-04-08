import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=10000)
def get_country_from_ip(ip: str) -> str:
    """
    Get country code from IP address using geoip2.
    Falls back to 'UNKNOWN' if geoip2 is not available or IP is local.
    Uses MaxMind GeoLite2 database (requires mmdb file).
    """
    # Skip private/local IPs
    if ip.startswith(("127.", "192.168.", "10.", "172.")):
        return "LOCAL"

    try:
        import geoip2.database

        # Path to MaxMind GeoLite2-Country.mmdb database
        db_path = os.getenv("GEOIP_DB_PATH", "/app/data/GeoLite2-Country.mmdb")

        if not os.path.exists(db_path):
            logger.debug(f"GeoIP database not found at {db_path}")
            return "UNKNOWN"

        reader = geoip2.database.Reader(db_path)
        response = reader.country(ip)
        country = response.country.iso_code
        return country or "UNKNOWN"
    except ImportError:
        return "UNKNOWN"
    except Exception as e:
        logger.debug(f"GeoIP lookup failed for {ip}: {e}")
        return "UNKNOWN"


def extract_client_ip(request) -> str:
    """
    Extract client IP from request, checking X-Forwarded-For header first (behind proxy).
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, use the first one (client IP)
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "UNKNOWN"
