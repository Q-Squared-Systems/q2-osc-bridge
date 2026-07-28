"""Base entity helpers for Q2 OSC Bridge mappings."""

from __future__ import annotations

import logging

from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .endpoint import Q2OscEndpoint
from .entity_mapping import OscEntityMapping

_LOGGER = logging.getLogger(__name__)


class Q2OscMappingEntity(Entity):
    """Base class for OSC mapping entities."""

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
        self._remove_listener = None

    async def async_added_to_hass(self) -> None:
        """Subscribe to messages after the entity is added."""
        await super().async_added_to_hass()
        if self.mapping.receive_address:
            self._remove_listener = self.endpoint.add_message_listener(
                self._handle_endpoint_message
            )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe when the entity is removed."""
        if self._remove_listener is not None:
            self._remove_listener()
            self._remove_listener = None
        await super().async_will_remove_from_hass()

    def _handle_endpoint_message(self, event_data: dict[str, object]) -> None:
        """Apply a matching incoming OSC message."""
        if event_data["address"] != self.mapping.receive_address:
            return
        arguments = event_data.get("arguments", [])
        if isinstance(arguments, list):
            try:
                self._apply_received_value(arguments[0] if arguments else None)
            except (TypeError, ValueError):
                _LOGGER.warning(
                    "Ignoring invalid value for OSC mapping %s",
                    self.mapping.name,
                )
            else:
                self.async_write_ha_state()

    def _apply_received_value(self, value: object) -> None:
        """Apply one decoded OSC argument to entity state."""
