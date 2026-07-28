"""Text platform for Q2 OSC Bridge string controls."""

from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .endpoint import Q2OscEndpoint
from .entity_base import Q2OscMappingEntity
from .entity_mapping import mappings_from_entry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up text mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in mappings_from_entry(entry) if m.platform == "text"]
    async_add_entities(Q2OscText(endpoint, mapping) for mapping in mappings)


class Q2OscText(Q2OscMappingEntity, TextEntity):
    """Text entity backed by OSC string values."""

    _attr_native_value = ""

    async def async_set_value(self, value: str) -> None:
        """Set and send the text value."""
        self._attr_native_value = value
        if self.mapping.send_address:
            await self.endpoint.async_send(self.mapping.send_address, [value])
        self.async_write_ha_state()

    def _apply_received_value(self, value: object) -> None:
        self._attr_native_value = str(value)
