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
        """Turn on and send OSC true."""
        self._attr_is_on = True
        if self.mapping.send_address:
            await self.endpoint.async_send(self.mapping.send_address, [True])
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn off and send OSC false."""
        self._attr_is_on = False
        if self.mapping.send_address:
            await self.endpoint.async_send(self.mapping.send_address, [False])
        self.async_write_ha_state()

    def _apply_received_value(self, value: object) -> None:
        self._attr_is_on = _as_bool(value)


def _as_bool(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().casefold() not in {"", "0", "false", "off", "no"}
    return bool(value)
