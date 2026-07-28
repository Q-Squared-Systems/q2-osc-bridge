"""Constants for Q2 OSC Bridge."""

from __future__ import annotations

DOMAIN = "q2_osc_bridge"
EVENT_OSC_MESSAGE = "q2_osc_bridge_message"

CONF_NAME = "name"
CONF_REMOTE_HOST = "remote_host"
CONF_REMOTE_PORT = "remote_port"
CONF_RECEIVE_ENABLED = "receive_enabled"
CONF_LOCAL_BIND_ADDRESS = "local_bind_address"
CONF_LOCAL_PORT = "local_port"
CONF_ALLOWED_SOURCE_IPS = "allowed_source_ips"
CONF_MAPPINGS = "mappings"
CONF_PLATFORM = "platform"
CONF_SEND_ADDRESS = "send_address"
CONF_RECEIVE_ADDRESS = "receive_address"
CONF_OPTIONS = "options"
CONF_MIN_VALUE = "min_value"
CONF_MAX_VALUE = "max_value"
CONF_STEP = "step"
CONF_OSC_TYPE = "osc_type"

DEFAULT_BIND_ADDRESS = "0.0.0.0"
DEFAULT_RECEIVE_ENABLED = True

SERVICE_SEND = "send"
ATTR_ADDRESS = "address"
ATTR_ARGUMENTS = "arguments"
ATTR_ENDPOINT = "endpoint"
ATTR_CONFIG_ENTRY_ID = "config_entry_id"

PLATFORMS = [
    "number",
    "switch",
    "button",
    "sensor",
    "binary_sensor",
    "select",
    "text",
]

MAPPING_PLATFORMS = tuple(PLATFORMS)
