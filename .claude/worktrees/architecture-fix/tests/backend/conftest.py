import os
from unittest.mock import patch, MagicMock

# Set up dummy MySQL config before any kirinchat.database imports
_dummy_mysql = {
    "endpoint": "sqlite:///test.db",
    "async_endpoint": "sqlite+aiosqlite:///test.db",
}


def _patch_settings():
    """Patch app_settings.mysql before database module initializes engine."""
    import kirinchat.settings as settings_mod
    if not settings_mod.app_settings.mysql.get("endpoint"):
        settings_mod.app_settings.mysql = _dummy_mysql


_patch_settings()
