from __future__ import annotations

import pytest
import voluptuous as vol
from voluptuous_serialize import convert

from custom_components.q2_osc_bridge.const import DEFAULT_BIND_ADDRESS
from custom_components.q2_osc_bridge.target_settings import target_settings_from_entry
from custom_components.q2_osc_bridge.validators import (
    PORT_SCHEMA,
    normalize_allowed_source_ips,
    normalize_osc_arguments,
    validate_osc_address,
    validate_port,
)


def test_default_bind_address_listens_on_all_interfaces() -> None:
    assert DEFAULT_BIND_ADDRESS == "0.0.0.0"


def test_target_settings_defaults_include_option_overrides() -> None:
    entry = type(
        "Entry",
        (),
        {
            "data": {
                "name": "Original",
                "remote_host": "192.0.2.10",
                "remote_port": 9000,
                "receive_enabled": True,
                "local_bind_address": "0.0.0.0",
                "local_port": 9001,
                "allowed_source_ips": [],
            },
            "options": {
                "name": "MadMapper",
                "remote_host": "192.0.2.20",
                "remote_port": 8000,
            },
        },
    )()

    defaults = target_settings_from_entry(entry)

    assert defaults["name"] == "MadMapper"
    assert defaults["remote_host"] == "192.0.2.20"
    assert defaults["remote_port"] == 8000
    assert defaults["local_bind_address"] == "0.0.0.0"


def test_port_schema_is_config_flow_serializable() -> None:
    schema = vol.Schema({vol.Required("port", default=9000): PORT_SCHEMA})

    assert convert(schema)


def test_validate_port_accepts_udp_range() -> None:
    assert validate_port("1") == 1
    assert validate_port(65535) == 65535


@pytest.mark.parametrize("port", [0, 65536])
def test_validate_port_rejects_out_of_range(port: int) -> None:
    with pytest.raises(vol.Invalid):
        validate_port(port)


def test_normalize_allowed_source_ips_accepts_csv() -> None:
    assert normalize_allowed_source_ips("192.168.1.10, 10.0.0.5") == [
        "192.168.1.10",
        "10.0.0.5",
    ]


def test_normalize_allowed_source_ips_rejects_invalid_ip() -> None:
    with pytest.raises(vol.Invalid):
        normalize_allowed_source_ips("192.168.1.999")


def test_normalize_osc_arguments_accepts_scalar_and_list() -> None:
    assert normalize_osc_arguments(7) == [7]
    assert normalize_osc_arguments([1, 2.5, "go", True, None]) == [
        1,
        2.5,
        "go",
        True,
        None,
    ]


def test_normalize_osc_arguments_rejects_objects() -> None:
    with pytest.raises(vol.Invalid):
        normalize_osc_arguments({"bad": "shape"})


def test_validate_osc_address_requires_slash() -> None:
    assert validate_osc_address("/q2/test") == "/q2/test"
    with pytest.raises(vol.Invalid):
        validate_osc_address("q2/test")
