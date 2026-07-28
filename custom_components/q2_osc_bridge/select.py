"""Select platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
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
    """Set up select mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in mappings_from_entry(entry) if m.platform == "select"]
    async_add_entities(Q2OscSelect(endpoint, mapping) for mapping in mappings)


class Q2OscSelect(Q2OscMappingEntity, SelectEntity):
    """Select backed by OSC string values."""

    def __init__(
        self,
        endpoint: Q2OscEndpoint,
        mapping: OscEntityMapping,
    ) -> None:
        super().__init__(endpoint, mapping)
        self._attr_options = mapping.options
        self._attr_current_option = mapping.options[0]

    async def async_select_option(self, option: str) -> None:
        """Select and send an option."""
        self._attr_current_option = option
        if self.mapping.send_address:
            await self.endpoint.async_send(self.mapping.send_address, [option])
        self.async_write_ha_state()

    def _apply_received_value(self, value: object) -> None:
        option = str(value)
        if option in self._attr_options:
            self._attr_current_option = option
