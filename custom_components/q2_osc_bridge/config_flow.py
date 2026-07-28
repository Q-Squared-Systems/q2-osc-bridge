"""Config flow for Q2 OSC Bridge."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_ALLOWED_SOURCE_IPS,
    CONF_LOCAL_BIND_ADDRESS,
    CONF_LOCAL_PORT,
    CONF_NAME,
    CONF_RECEIVE_ENABLED,
    CONF_REMOTE_HOST,
    CONF_REMOTE_PORT,
    DEFAULT_BIND_ADDRESS,
    DEFAULT_RECEIVE_ENABLED,
    DOMAIN,
)
from .validators import PORT_SCHEMA, normalize_allowed_source_ips, validate_port


class Q2OscBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Q2 OSC Bridge."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Create an OSC endpoint."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                data = _validate_user_input(user_input)
            except vol.Invalid:
                errors["base"] = "invalid_config"
            else:
                await self.async_set_unique_id(
                    f"{data[CONF_LOCAL_BIND_ADDRESS]}:{data[CONF_LOCAL_PORT]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=data[CONF_NAME], data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input),
            errors=errors,
        )


def _user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Return the endpoint form schema."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "OSC Endpoint")): str,
            vol.Required(
                CONF_REMOTE_HOST,
                default=defaults.get(CONF_REMOTE_HOST, defaults.get(CONF_HOST, "")),
            ): str,
            vol.Required(
                CONF_REMOTE_PORT,
                default=defaults.get(CONF_REMOTE_PORT, 9000),
            ): PORT_SCHEMA,
            vol.Required(
                CONF_RECEIVE_ENABLED,
                default=defaults.get(CONF_RECEIVE_ENABLED, DEFAULT_RECEIVE_ENABLED),
            ): bool,
            vol.Required(
                CONF_LOCAL_BIND_ADDRESS,
                default=defaults.get(CONF_LOCAL_BIND_ADDRESS, DEFAULT_BIND_ADDRESS),
            ): str,
            vol.Required(
                CONF_LOCAL_PORT,
                default=defaults.get(CONF_LOCAL_PORT, 9001),
            ): PORT_SCHEMA,
            vol.Optional(
                CONF_ALLOWED_SOURCE_IPS,
                default=", ".join(defaults.get(CONF_ALLOWED_SOURCE_IPS, [])),
            ): str,
        }
    )


def _validate_user_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize endpoint form input."""
    name = str(user_input[CONF_NAME]).strip()
    remote_host = str(user_input[CONF_REMOTE_HOST]).strip()
    local_bind_address = str(user_input[CONF_LOCAL_BIND_ADDRESS]).strip()

    if not name:
        raise vol.Invalid("name is required")
    if not remote_host:
        raise vol.Invalid("remote host is required")
    if not local_bind_address:
        raise vol.Invalid("local bind address is required")

    return {
        CONF_NAME: name,
        CONF_REMOTE_HOST: remote_host,
        CONF_REMOTE_PORT: validate_port(user_input[CONF_REMOTE_PORT]),
        CONF_RECEIVE_ENABLED: bool(user_input[CONF_RECEIVE_ENABLED]),
        CONF_LOCAL_BIND_ADDRESS: local_bind_address,
        CONF_LOCAL_PORT: validate_port(user_input[CONF_LOCAL_PORT]),
        CONF_ALLOWED_SOURCE_IPS: normalize_allowed_source_ips(
            user_input.get(CONF_ALLOWED_SOURCE_IPS)
        ),
    }
