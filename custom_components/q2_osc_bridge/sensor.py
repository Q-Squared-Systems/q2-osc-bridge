"""Sensor platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    """Set up sensor mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in mappings_from_entry(entry) if m.platform == "sensor"]
    async_add_entities(Q2OscSensor(endpoint, mapping) for mapping in mappings)


class Q2OscSensor(Q2OscMappingEntity, SensorEntity):
    """Sensor updated by incoming OSC messages."""

    _attr_native_value = None

    def _apply_received_value(self, value: object) -> None:
        self._attr_native_value = value
