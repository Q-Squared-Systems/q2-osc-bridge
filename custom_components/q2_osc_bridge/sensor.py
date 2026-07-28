"""Sensor platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    """Set up placeholder sensor mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in default_mappings(endpoint.name) if m.platform == "sensor"]
    async_add_entities(Q2OscSensor(endpoint, mapping) for mapping in mappings)


class Q2OscSensor(Q2OscMappingEntity, SensorEntity):
    """Placeholder sensor for future receive mappings."""

    @property
    def native_value(self) -> str | None:
        """Return the endpoint last message time for now."""
        return self.endpoint.diagnostics.last_message_time
