"""Binary sensor platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Set up placeholder binary sensor mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in default_mappings(endpoint.name) if m.platform == "binary_sensor"]
    async_add_entities(Q2OscBinarySensor(endpoint, mapping) for mapping in mappings)


class Q2OscBinarySensor(Q2OscMappingEntity, BinarySensorEntity):
    """Placeholder binary sensor for future receive mappings."""

    @property
    def is_on(self) -> bool:
        """Return whether this endpoint has received at least one message."""
        return self.endpoint.diagnostics.received_messages > 0
