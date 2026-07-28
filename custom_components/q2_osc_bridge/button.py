"""Button platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up button mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in mappings_from_entry(entry) if m.platform == "button"]
    async_add_entities(Q2OscButton(endpoint, mapping) for mapping in mappings)


class Q2OscButton(Q2OscMappingEntity, ButtonEntity):
    """Button that sends an OSC message."""

    async def async_press(self) -> None:
        """Send the mapped OSC message."""
        if self.mapping.send_address:
            await self.endpoint.async_send(self.mapping.send_address)
