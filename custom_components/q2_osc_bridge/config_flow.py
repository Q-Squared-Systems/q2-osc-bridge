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
    CONF_MAPPINGS,
    CONF_MAX_VALUE,
    CONF_MIN_VALUE,
    CONF_NAME,
    CONF_RECEIVE_ADDRESS,
    CONF_RECEIVE_ENABLED,
    CONF_REMOTE_HOST,
    CONF_REMOTE_PORT,
    CONF_SEND_ADDRESS,
    CONF_STEP,
    DEFAULT_BIND_ADDRESS,
    DEFAULT_RECEIVE_ENABLED,
    DOMAIN,
)
from .entity_mapping import (
    OscEntityMapping,
    create_button_mapping,
    create_number_mapping,
    create_sensor_mapping,
    create_switch_mapping,
    create_text_mapping,
)
from .target_settings import target_settings_from_entry
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
        menu_options = {
            "target_settings": "Edit target settings",
            "add_mapping": "Add button control",
            "add_number_mapping": "Add float control",
            "add_integer_mapping": "Add integer control",
            "add_switch_mapping": "Add boolean control",
            "add_text_mapping": "Add string control",
            "add_sensor_mapping": "Add sensor monitor",
        }
        if self.config_entry.options.get(CONF_MAPPINGS):
            menu_options["remove_mapping"] = "Remove entity mapping"
        return self.async_show_menu(step_id="init", menu_options=menu_options)

    async def async_step_target_settings(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Edit OSC target settings."""
        errors: dict[str, str] = {}
        defaults = target_settings_from_entry(self.config_entry)
        if user_input is not None:
            try:
                settings = _validate_user_input(user_input)
            except vol.Invalid:
                errors["base"] = "invalid_config"
            else:
                return self.async_create_entry(
                    title="",
                    data={**self.config_entry.options, **settings},
                )

        return self.async_show_form(
            step_id="target_settings",
            data_schema=_user_schema(user_input or defaults),
            errors=errors,
        )

    async def async_step_add_mapping(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Add one button entity mapping."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                mapping = _mapping_from_user_input(user_input)
            except (ValueError, vol.Invalid):
                errors["base"] = "invalid_mapping"
            else:
                mappings = list(self.config_entry.options.get(CONF_MAPPINGS, []))
                return self._async_create_mapping_entry(mappings, mapping)

        return self.async_show_form(
            step_id="add_mapping",
            data_schema=_button_mapping_schema(user_input),
            errors=errors,
        )

    async def async_step_add_number_mapping(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Add one float number entity mapping."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                mapping = _number_mapping_from_user_input(user_input)
            except (ValueError, vol.Invalid):
                errors["base"] = "invalid_mapping"
            else:
                mappings = list(self.config_entry.options.get(CONF_MAPPINGS, []))
                return self._async_create_mapping_entry(mappings, mapping)

        return self.async_show_form(
            step_id="add_number_mapping",
            data_schema=_number_mapping_schema(user_input),
            errors=errors,
        )

    async def async_step_add_integer_mapping(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Add one integer number entity mapping."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                mapping = _integer_mapping_from_user_input(user_input)
            except (ValueError, vol.Invalid):
                errors["base"] = "invalid_mapping"
            else:
                mappings = list(self.config_entry.options.get(CONF_MAPPINGS, []))
                return self._async_create_mapping_entry(mappings, mapping)

        return self.async_show_form(
            step_id="add_integer_mapping",
            data_schema=_integer_mapping_schema(user_input),
            errors=errors,
        )

    async def async_step_add_switch_mapping(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Add one boolean switch entity mapping."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                mapping = _switch_mapping_from_user_input(user_input)
            except (ValueError, vol.Invalid):
                errors["base"] = "invalid_mapping"
            else:
                mappings = list(self.config_entry.options.get(CONF_MAPPINGS, []))
                return self._async_create_mapping_entry(mappings, mapping)

        return self.async_show_form(
            step_id="add_switch_mapping",
            data_schema=_send_receive_mapping_schema(user_input),
            errors=errors,
        )

    async def async_step_add_text_mapping(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Add one string text entity mapping."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                mapping = _text_mapping_from_user_input(user_input)
            except (ValueError, vol.Invalid):
                errors["base"] = "invalid_mapping"
            else:
                mappings = list(self.config_entry.options.get(CONF_MAPPINGS, []))
                return self._async_create_mapping_entry(mappings, mapping)

        return self.async_show_form(
            step_id="add_text_mapping",
            data_schema=_send_receive_mapping_schema(user_input),
            errors=errors,
        )

    async def async_step_add_sensor_mapping(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Add one sensor entity mapping."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                mapping = _sensor_mapping_from_user_input(user_input)
            except (ValueError, vol.Invalid):
                errors["base"] = "invalid_mapping"
            else:
                mappings = list(self.config_entry.options.get(CONF_MAPPINGS, []))
                return self._async_create_mapping_entry(mappings, mapping)

        return self.async_show_form(
            step_id="add_sensor_mapping",
            data_schema=_sensor_mapping_schema(user_input),
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

    def _async_create_mapping_entry(
        self,
        mappings: list[dict[str, Any]],
        mapping: OscEntityMapping,
    ) -> FlowResult:
        """Append a mapping and finish the options flow."""
        mappings.append(mapping.as_dict())
        return self.async_create_entry(
            title="",
            data={**self.config_entry.options, CONF_MAPPINGS: mappings},
        )


def _button_mapping_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Return the button entity mapping form."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
            vol.Required(
                CONF_SEND_ADDRESS,
                default=defaults.get(CONF_SEND_ADDRESS, ""),
            ): str,
        }
    )


def _sensor_mapping_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Return the sensor entity mapping form."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
            vol.Required(
                CONF_RECEIVE_ADDRESS,
                default=defaults.get(CONF_RECEIVE_ADDRESS, ""),
            ): str,
        }
    )


def _number_mapping_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Return the float number entity mapping form."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
            vol.Required(
                CONF_SEND_ADDRESS,
                default=defaults.get(CONF_SEND_ADDRESS, ""),
            ): str,
            vol.Optional(
                CONF_RECEIVE_ADDRESS,
                default=defaults.get(CONF_RECEIVE_ADDRESS, ""),
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


def _integer_mapping_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Return the integer number entity mapping form."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
            vol.Required(
                CONF_SEND_ADDRESS,
                default=defaults.get(CONF_SEND_ADDRESS, ""),
            ): str,
            vol.Optional(
                CONF_RECEIVE_ADDRESS,
                default=defaults.get(CONF_RECEIVE_ADDRESS, ""),
            ): str,
            vol.Optional(
                CONF_MIN_VALUE,
                default=defaults.get(CONF_MIN_VALUE, 0),
            ): vol.Coerce(int),
            vol.Optional(
                CONF_MAX_VALUE,
                default=defaults.get(CONF_MAX_VALUE, 100),
            ): vol.Coerce(int),
        }
    )


def _send_receive_mapping_schema(
    defaults: dict[str, Any] | None = None,
) -> vol.Schema:
    """Return a send/optional receive mapping form."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
            vol.Required(
                CONF_SEND_ADDRESS,
                default=defaults.get(CONF_SEND_ADDRESS, ""),
            ): str,
            vol.Optional(
                CONF_RECEIVE_ADDRESS,
                default=defaults.get(CONF_RECEIVE_ADDRESS, ""),
            ): str,
        }
    )


def _mapping_from_user_input(user_input: dict[str, Any]) -> OscEntityMapping:
    """Validate and normalize a mapping form submission."""
    return create_button_mapping(
        name=str(user_input[CONF_NAME]),
        target_path=str(user_input.get(CONF_SEND_ADDRESS, "")),
    )


def _number_mapping_from_user_input(user_input: dict[str, Any]) -> OscEntityMapping:
    """Validate and normalize a float number mapping form submission."""
    return create_number_mapping(
        name=str(user_input[CONF_NAME]),
        target_path=str(user_input.get(CONF_SEND_ADDRESS, "")),
        source_path=str(user_input.get(CONF_RECEIVE_ADDRESS, "")),
        min_value=float(user_input.get(CONF_MIN_VALUE, 0)),
        max_value=float(user_input.get(CONF_MAX_VALUE, 100)),
        step=float(user_input.get(CONF_STEP, 1)),
        osc_type="f",
    )


def _integer_mapping_from_user_input(user_input: dict[str, Any]) -> OscEntityMapping:
    """Validate and normalize an integer number mapping form submission."""
    return create_number_mapping(
        name=str(user_input[CONF_NAME]),
        target_path=str(user_input.get(CONF_SEND_ADDRESS, "")),
        source_path=str(user_input.get(CONF_RECEIVE_ADDRESS, "")),
        min_value=int(user_input.get(CONF_MIN_VALUE, 0)),
        max_value=int(user_input.get(CONF_MAX_VALUE, 100)),
        step=1,
        osc_type="i",
    )


def _switch_mapping_from_user_input(user_input: dict[str, Any]) -> OscEntityMapping:
    """Validate and normalize a boolean switch mapping form submission."""
    return create_switch_mapping(
        name=str(user_input[CONF_NAME]),
        target_path=str(user_input.get(CONF_SEND_ADDRESS, "")),
        source_path=str(user_input.get(CONF_RECEIVE_ADDRESS, "")),
    )


def _text_mapping_from_user_input(user_input: dict[str, Any]) -> OscEntityMapping:
    """Validate and normalize a string text mapping form submission."""
    return create_text_mapping(
        name=str(user_input[CONF_NAME]),
        target_path=str(user_input.get(CONF_SEND_ADDRESS, "")),
        source_path=str(user_input.get(CONF_RECEIVE_ADDRESS, "")),
    )


def _sensor_mapping_from_user_input(user_input: dict[str, Any]) -> OscEntityMapping:
    """Validate and normalize a sensor mapping form submission."""
    return create_sensor_mapping(
        name=str(user_input[CONF_NAME]),
        source_path=str(user_input.get(CONF_RECEIVE_ADDRESS, "")),
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
