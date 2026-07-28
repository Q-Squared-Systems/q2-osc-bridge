"""Base entity helpers for Q2 OSC Bridge mapping scaffolding."""

from __future__ import annotations

from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .endpoint import Q2OscEndpoint
from .entity_mapping import OscEntityMapping


class Q2OscMappingEntity(Entity):
    """Base class for placeholder OSC mapping entities."""

    _attr_has_entity_name = True

    def __init__(self, endpoint: Q2OscEndpoint, mapping: OscEntityMapping) -> None:
        self.endpoint = endpoint
        self.mapping = mapping
        self._attr_name = mapping.name
        self._attr_unique_id = f"{endpoint.entry_id}_{mapping.platform}_{mapping.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, endpoint.entry_id)},
            "name": endpoint.name,
            "manufacturer": "Q Squared",
            "model": "OSC Endpoint",
        }
