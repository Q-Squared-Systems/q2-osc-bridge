"""Switch platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .endpoint import Q2OscEndpoint
from .entity_base import Q2OscMappingEntity
from .entity_mapping import mappings_from_entry
from .switch_encoding import as_bool, osc_switch_value


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in mappings_from_entry(entry) if m.platform == "switch"]
    async_add_entities(Q2OscSwitch(endpoint, mapping) for mapping in mappings)


class Q2OscSwitch(Q2OscMappingEntity, SwitchEntity):
    """Switch backed by OSC boolean values."""

    _attr_is_on = False

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn on and send the configured OSC true value."""
        self._attr_is_on = True
        if self.mapping.send_address:
            await self.endpoint.async_send(
                self.mapping.send_address,
                [osc_switch_value(True, self.mapping.osc_type)],
            )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn off and send the configured OSC false value."""
        self._attr_is_on = False
        if self.mapping.send_address:
            await self.endpoint.async_send(
                self.mapping.send_address,
                [osc_switch_value(False, self.mapping.osc_type)],
            )
        self.async_write_ha_state()

    def _apply_received_value(self, value: object) -> None:
        self._attr_is_on = as_bool(value, self.mapping.osc_type)
