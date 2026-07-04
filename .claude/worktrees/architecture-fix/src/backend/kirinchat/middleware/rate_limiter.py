"""
Rate-limiting configuration using slowapi.

Lives in its own module to avoid circular imports (main.py -> router -> interview.py -> main).
"""

from functools import lru_cache

from slowapi import Limiter
from slowapi.util import get_remote_address

from kirinchat.settings import app_settings


def _get_real_ip(request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For behind a reverse proxy."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # First IP in the chain is the original client
        return forwarded.split(",")[0].strip()
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip.strip()
    return get_remote_address(request)


def _get_storage_uri() -> str:
    """Return the Redis URI for shared rate-limit storage, or empty string for in-memory."""
    try:
        uri = app_settings.redis.get("endpoint", "")
        if uri:
            return uri
    except Exception:
        pass
    return "memory://"


# --- Rate limit constants (centralised for easy tuning) ---
RATE_LIMIT_DEFAULT = "60/minute"
RATE_LIMIT_INTERVIEW_START = "10/minute"
RATE_LIMIT_INTERVIEW_ANSWER = "20/minute"
RATE_LIMIT_INTERVIEW_COMPLETE = "5/minute"
RATE_LIMIT_EVALUATION_PDF = "3/minute"


@lru_cache(maxsize=1)
def get_limiter() -> Limiter:
    """Return the application-wide Limiter (singleton)."""
    return Limiter(
        key_func=_get_real_ip,
        default_limits=[RATE_LIMIT_DEFAULT],
        storage_uri=_get_storage_uri(),
    )


# Module-level limiter instance (used by route decorators).
limiter: Limiter = get_limiter()
