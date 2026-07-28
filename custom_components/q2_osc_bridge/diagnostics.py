"""Diagnostics support for Q2 OSC Bridge."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .endpoint import Q2OscEndpoint


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    endpoint: Q2OscEndpoint | None = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    return {
        "entry": {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "data": dict(entry.data),
        },
        "diagnostics": endpoint.diagnostics.as_dict() if endpoint else {},
    }
