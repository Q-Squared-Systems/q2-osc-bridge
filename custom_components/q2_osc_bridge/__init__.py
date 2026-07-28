"""Q2 OSC Bridge integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import voluptuous as vol

try:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall
    from homeassistant.helpers import config_validation as cv
except ModuleNotFoundError:
    ConfigEntry = Any
    HomeAssistant = Any
    ServiceCall = Any

    class _ConfigValidationFallback:
        string: Callable[[Any], str] = str

    cv = _ConfigValidationFallback()

from .const import (
    ATTR_ADDRESS,
    ATTR_ARGUMENTS,
    ATTR_CONFIG_ENTRY_ID,
    ATTR_ENDPOINT,
    CONF_ALLOWED_SOURCE_IPS,
    CONF_LOCAL_BIND_ADDRESS,
    CONF_LOCAL_PORT,
    CONF_NAME,
    CONF_RECEIVE_ENABLED,
    CONF_REMOTE_HOST,
    CONF_REMOTE_PORT,
    DOMAIN,
    PLATFORMS,
    SERVICE_SEND,
)
from .endpoint import EndpointConfig, Q2OscEndpoint
from .validators import normalize_osc_arguments, validate_osc_address

_LOGGER = logging.getLogger(__name__)

SEND_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ADDRESS): validate_osc_address,
        vol.Optional(ATTR_ARGUMENTS): normalize_osc_arguments,
        vol.Optional(ATTR_ENDPOINT): cv.string,
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up integration-level services."""
    hass.data.setdefault(DOMAIN, {})

    async def async_handle_send(call: ServiceCall) -> None:
        endpoint = _resolve_endpoint(hass, call)
        if endpoint is None:
            raise vol.Invalid("No matching Q2 OSC Bridge endpoint found")
        await endpoint.async_send(
            call.data[ATTR_ADDRESS],
            call.data.get(ATTR_ARGUMENTS),
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND,
        async_handle_send,
        schema=SEND_SERVICE_SCHEMA,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one configured OSC endpoint."""
    endpoint = Q2OscEndpoint(hass, _endpoint_config_from_entry(entry))
    await endpoint.async_start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = endpoint
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload one OSC endpoint."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        endpoint: Q2OscEndpoint | None = hass.data[DOMAIN].pop(entry.entry_id, None)
        if endpoint is not None:
            await endpoint.async_stop()
    return unloaded


def _endpoint_config_from_entry(entry: ConfigEntry) -> EndpointConfig:
    """Convert a config entry to runtime endpoint config."""
    data = entry.data
    return EndpointConfig(
        entry_id=entry.entry_id,
        name=data[CONF_NAME],
        remote_host=data[CONF_REMOTE_HOST],
        remote_port=data[CONF_REMOTE_PORT],
        receive_enabled=data[CONF_RECEIVE_ENABLED],
        local_bind_address=data[CONF_LOCAL_BIND_ADDRESS],
        local_port=data[CONF_LOCAL_PORT],
        allowed_source_ips=list(data.get(CONF_ALLOWED_SOURCE_IPS, [])),
    )


def _resolve_endpoint(
    hass: HomeAssistant,
    call: ServiceCall,
) -> Q2OscEndpoint | None:
    """Resolve a send service call to a configured endpoint."""
    endpoints: dict[str, Q2OscEndpoint] = hass.data.get(DOMAIN, {})
    if not endpoints:
        return None

    entry_id = call.data.get(ATTR_CONFIG_ENTRY_ID)
    if entry_id:
        return endpoints.get(entry_id)

    endpoint_name = call.data.get(ATTR_ENDPOINT)
    if endpoint_name:
        for endpoint in endpoints.values():
            if endpoint.name == endpoint_name or endpoint.entry_id == endpoint_name:
                return endpoint
        return None

    if len(endpoints) == 1:
        return next(iter(endpoints.values()))

    _LOGGER.warning("Multiple OSC endpoints exist; include endpoint or config_entry_id")
    return None
