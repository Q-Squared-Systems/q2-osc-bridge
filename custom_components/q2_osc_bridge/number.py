"""Number platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .endpoint import Q2OscEndpoint
from .entity_base import Q2OscMappingEntity
from .entity_mapping import OscEntityMapping, mappings_from_entry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in mappings_from_entry(entry) if m.platform == "number"]
    async_add_entities(Q2OscNumber(endpoint, mapping) for mapping in mappings)


class Q2OscNumber(Q2OscMappingEntity, NumberEntity):
    """Number backed by OSC values."""

    def __init__(
        self,
        endpoint: Q2OscEndpoint,
        mapping: OscEntityMapping,
    ) -> None:
        super().__init__(endpoint, mapping)
        self._attr_native_min_value = mapping.min_value
        self._attr_native_max_value = mapping.max_value
        self._attr_native_step = mapping.step
        self._attr_native_value = mapping.initial_value or mapping.min_value

    async def async_set_native_value(self, value: float) -> None:
        """Set and send the number value."""
        value = self._coerce_value(value)
        self._attr_native_value = value
        if self.mapping.send_address:
            await self.endpoint.async_send(self.mapping.send_address, [value])
        self.async_write_ha_state()

    def _apply_received_value(self, value: object) -> None:
        self._attr_native_value = self._coerce_value(value)

    def _coerce_value(self, value: object) -> int | float:
        """Coerce values to the configured OSC number type."""
        if self.mapping.osc_type == "i":
            return int(round(float(value)))
        return float(value)
