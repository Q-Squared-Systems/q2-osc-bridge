"""Switch platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
    """Set up placeholder switch mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in default_mappings(endpoint.name) if m.platform == "switch"]
    async_add_entities(Q2OscSwitch(endpoint, mapping) for mapping in mappings)


class Q2OscSwitch(Q2OscMappingEntity, SwitchEntity):
    """Placeholder switch for future send/receive mappings."""

    _attr_is_on = True

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn the placeholder switch on."""
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn the placeholder switch off."""
        self._attr_is_on = False
