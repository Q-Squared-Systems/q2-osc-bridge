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
    from homeassistant.helpers import device_registry as dr
except ModuleNotFoundError:
    ConfigEntry = Any
    HomeAssistant = Any
    ServiceCall = Any
    dr = None

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
from .target_settings import target_settings_from_entry
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
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload one OSC endpoint."""
    endpoint: Q2OscEndpoint | None = hass.data[DOMAIN].pop(entry.entry_id, None)
    if endpoint is not None:
        await endpoint.async_stop()

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unloaded and endpoint is not None:
        hass.data[DOMAIN][entry.entry_id] = endpoint
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload an endpoint after its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _endpoint_config_from_entry(entry: ConfigEntry) -> EndpointConfig:
    """Convert a config entry to runtime endpoint config."""
    data = target_settings_from_entry(entry)
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
        normalized_name = _normalize_endpoint_name(endpoint_name)
        for endpoint in endpoints.values():
            if normalized_name in _endpoint_aliases(hass, endpoint):
                return endpoint
        return None

    if len(endpoints) == 1:
        return next(iter(endpoints.values()))

    _LOGGER.warning("Multiple OSC endpoints exist; include endpoint or config_entry_id")
    return None


def _endpoint_aliases(
    hass: HomeAssistant,
    endpoint: Q2OscEndpoint,
) -> set[str]:
    """Return normalized names that can identify an endpoint."""
    aliases = {endpoint.name, endpoint.entry_id}

    entry = hass.config_entries.async_get_entry(endpoint.entry_id)
    if entry is not None:
        aliases.add(entry.title)

    if dr is not None:
        device = dr.async_get(hass).async_get_device(
            identifiers={(DOMAIN, endpoint.entry_id)}
        )
        if device is not None:
            aliases.update(name for name in (device.name_by_user, device.name) if name)

    return {_normalize_endpoint_name(alias) for alias in aliases}


def _normalize_endpoint_name(value: Any) -> str:
    """Normalize an endpoint selector for user-friendly matching."""
    return str(value).strip().casefold()
