"""Helpers for persisted OSC target settings."""

from __future__ import annotations

from typing import Any

from .const import (
    CONF_ALLOWED_SOURCE_IPS,
    CONF_LOCAL_BIND_ADDRESS,
    CONF_LOCAL_PORT,
    CONF_NAME,
    CONF_RECEIVE_ENABLED,
    CONF_REMOTE_HOST,
    CONF_REMOTE_PORT,
)

TARGET_SETTING_KEYS = (
    CONF_NAME,
    CONF_REMOTE_HOST,
    CONF_REMOTE_PORT,
    CONF_RECEIVE_ENABLED,
    CONF_LOCAL_BIND_ADDRESS,
    CONF_LOCAL_PORT,
    CONF_ALLOWED_SOURCE_IPS,
)


def target_settings_from_entry(entry: Any) -> dict[str, Any]:
    """Return target settings with options overriding initial config data."""
    return {
        **entry.data,
        **{
            key: entry.options[key]
            for key in TARGET_SETTING_KEYS
            if key in entry.options
        },
    }
