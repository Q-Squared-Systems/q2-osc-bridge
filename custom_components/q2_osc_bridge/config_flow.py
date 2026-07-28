"""Config flow for Q2 OSC Bridge."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_ALLOWED_SOURCE_IPS,
    CONF_LOCAL_BIND_ADDRESS,
    CONF_LOCAL_PORT,
    CONF_MAPPINGS,
    CONF_MAX_VALUE,
    CONF_MIN_VALUE,
    CONF_NAME,
    CONF_OPTIONS,
    CONF_PLATFORM,
    CONF_RECEIVE_ADDRESS,
    CONF_RECEIVE_ENABLED,
    CONF_REMOTE_HOST,
    CONF_REMOTE_PORT,
    CONF_SEND_ADDRESS,
    CONF_STEP,
    DEFAULT_BIND_ADDRESS,
    DEFAULT_RECEIVE_ENABLED,
    DOMAIN,
    MAPPING_PLATFORMS,
)
from .entity_mapping import OscEntityMapping
from .validators import PORT_SCHEMA, normalize_allowed_source_ips, validate_port


class Q2OscBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Q2 OSC Bridge."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the entity mapping options flow."""
        return Q2OscBridgeOptionsFlow()

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
            vol.Required(
                CONF_NAME, default=defaults.get(CONF_NAME, "OSC Endpoint")
            ): str,
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


class Q2OscBridgeOptionsFlow(config_entries.OptionsFlow):
    """Manage OSC entity mappings."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Show mapping management actions."""
        menu_options = ["add_mapping"]
        if self.config_entry.options.get(CONF_MAPPINGS):
            menu_options.append("remove_mapping")
        return self.async_show_menu(step_id="init", menu_options=menu_options)

    async def async_step_add_mapping(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Add one OSC entity mapping."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                mapping = _mapping_from_user_input(user_input)
            except vol.Invalid:
                errors["base"] = "invalid_mapping"
            else:
                mappings = list(self.config_entry.options.get(CONF_MAPPINGS, []))
                mappings.append(mapping.as_dict())
                return self.async_create_entry(
                    title="",
                    data={**self.config_entry.options, CONF_MAPPINGS: mappings},
                )

        return self.async_show_form(
            step_id="add_mapping",
            data_schema=_mapping_schema(user_input),
            errors=errors,
        )

    async def async_step_remove_mapping(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Remove one OSC entity mapping."""
        mappings = list(self.config_entry.options.get(CONF_MAPPINGS, []))
        labels = {
            mapping["key"]: f"{mapping['name']} ({mapping['platform']})"
            for mapping in mappings
        }
        if user_input is not None:
            selected_key = user_input["mapping"]
            mappings = [
                mapping for mapping in mappings if mapping["key"] != selected_key
            ]
            return self.async_create_entry(
                title="",
                data={**self.config_entry.options, CONF_MAPPINGS: mappings},
            )

        return self.async_show_form(
            step_id="remove_mapping",
            data_schema=vol.Schema({vol.Required("mapping"): vol.In(labels)}),
        )


def _mapping_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Return the initial generic entity mapping form."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_PLATFORM,
                default=defaults.get(CONF_PLATFORM, "button"),
            ): vol.In(MAPPING_PLATFORMS),
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
            vol.Optional(
                CONF_SEND_ADDRESS,
                default=defaults.get(CONF_SEND_ADDRESS, ""),
            ): str,
            vol.Optional(
                CONF_RECEIVE_ADDRESS,
                default=defaults.get(CONF_RECEIVE_ADDRESS, ""),
            ): str,
            vol.Optional(
                CONF_OPTIONS,
                default=defaults.get(CONF_OPTIONS, ""),
            ): str,
            vol.Optional(
                CONF_MIN_VALUE,
                default=defaults.get(CONF_MIN_VALUE, 0),
            ): vol.Coerce(float),
            vol.Optional(
                CONF_MAX_VALUE,
                default=defaults.get(CONF_MAX_VALUE, 100),
            ): vol.Coerce(float),
            vol.Optional(
                CONF_STEP,
                default=defaults.get(CONF_STEP, 1),
            ): vol.All(vol.Coerce(float), vol.Range(min=0.000001)),
        }
    )


def _mapping_from_user_input(user_input: dict[str, Any]) -> OscEntityMapping:
    """Validate and normalize a mapping form submission."""
    platform = user_input[CONF_PLATFORM]
    name = str(user_input[CONF_NAME]).strip()
    send_address = str(user_input.get(CONF_SEND_ADDRESS, "")).strip() or None
    receive_address = str(user_input.get(CONF_RECEIVE_ADDRESS, "")).strip() or None
    options = [
        option.strip()
        for option in str(user_input.get(CONF_OPTIONS, "")).split(",")
        if option.strip()
    ]
    min_value = float(user_input.get(CONF_MIN_VALUE, 0))
    max_value = float(user_input.get(CONF_MAX_VALUE, 100))
    step = float(user_input.get(CONF_STEP, 1))

    if not name:
        raise vol.Invalid("mapping name is required")
    if send_address and not send_address.startswith("/"):
        raise vol.Invalid("send address must start with /")
    if receive_address and not receive_address.startswith("/"):
        raise vol.Invalid("receive address must start with /")
    if not send_address and not receive_address:
        raise vol.Invalid("a send or receive address is required")
    if platform == "button" and not send_address:
        raise vol.Invalid("button mappings require a send address")
    if platform in {"sensor", "binary_sensor"} and not receive_address:
        raise vol.Invalid(f"{platform} mappings require a receive address")
    if platform == "select" and not options:
        raise vol.Invalid("select mappings require options")
    if min_value >= max_value:
        raise vol.Invalid("minimum must be less than maximum")
    if step <= 0:
        raise vol.Invalid("step must be positive")

    return OscEntityMapping(
        platform=platform,
        key=uuid4().hex,
        name=name,
        send_address=send_address,
        receive_address=receive_address,
        options=options,
        min_value=min_value,
        max_value=max_value,
        step=step,
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
