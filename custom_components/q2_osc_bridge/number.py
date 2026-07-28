"""Number platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .endpoint import Q2OscEndpoint
from .entity_base import Q2OscMappingEntity
from .entity_mapping import default_mappings


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up placeholder number mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in default_mappings(endpoint.name) if m.platform == "number"]
    async_add_entities(Q2OscNumber(endpoint, mapping) for mapping in mappings)


class Q2OscNumber(Q2OscMappingEntity, NumberEntity):
    """Placeholder number for future send/receive mappings."""

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_value = 0

    async def async_set_native_value(self, value: float) -> None:
        """Set the placeholder value."""
        self._attr_native_value = value
