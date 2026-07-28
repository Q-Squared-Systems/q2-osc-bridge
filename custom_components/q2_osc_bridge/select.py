"""Select platform scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
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
    """Set up placeholder select mappings."""
    endpoint: Q2OscEndpoint = hass.data[DOMAIN][entry.entry_id]
    mappings = [m for m in default_mappings(endpoint.name) if m.platform == "select"]
    async_add_entities(Q2OscSelect(endpoint, mapping) for mapping in mappings)


class Q2OscSelect(Q2OscMappingEntity, SelectEntity):
    """Placeholder select for future send/receive mappings."""

    _attr_options = ["default"]
    _attr_current_option = "default"

    async def async_select_option(self, option: str) -> None:
        """Select the placeholder option."""
        self._attr_current_option = option
