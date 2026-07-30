from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import custom_components.q2_osc_bridge as integration
from custom_components.q2_osc_bridge.const import (
    ATTR_ENDPOINT,
    CONF_ALLOWED_SOURCE_IPS,
    CONF_LOCAL_BIND_ADDRESS,
    CONF_LOCAL_PORT,
    CONF_NAME,
    CONF_RECEIVE_ENABLED,
    CONF_REMOTE_HOST,
    CONF_REMOTE_PORT,
    DOMAIN,
)
from custom_components.q2_osc_bridge.endpoint import EndpointConfig, Q2OscEndpoint


class _ConfigEntries:
    def __init__(self, title: str) -> None:
        self._entry = SimpleNamespace(title=title)

    def async_get_entry(self, entry_id: str) -> Any:
        return self._entry if entry_id == "entry-1" else None


def _endpoint() -> Q2OscEndpoint:
    return Q2OscEndpoint(
        hass=None,
        config=EndpointConfig(
            entry_id="entry-1",
            name="OSC Endpoint",
            remote_host="127.0.0.1",
            remote_port=9000,
            receive_enabled=True,
            local_bind_address="127.0.0.1",
            local_port=9001,
        ),
    )


def _hass(title: str = "OSC Endpoint") -> Any:
    return SimpleNamespace(
        data={DOMAIN: {"entry-1": _endpoint()}},
        config_entries=_ConfigEntries(title),
    )


def test_resolve_endpoint_by_config_entry_title() -> None:
    hass = _hass(title="MadMapper")
    call = SimpleNamespace(data={ATTR_ENDPOINT: "  madmapper "})

    assert integration._resolve_endpoint(hass, call) is hass.data[DOMAIN]["entry-1"]


def test_resolve_endpoint_by_user_renamed_device(monkeypatch: Any) -> None:
    hass = _hass()
    device = SimpleNamespace(name_by_user="MadMapper", name="OSC Endpoint")
    registry = SimpleNamespace(
        async_get_device=lambda **kwargs: device,
    )
    monkeypatch.setattr(
        integration,
        "dr",
        SimpleNamespace(async_get=lambda requested_hass: registry),
    )
    call = SimpleNamespace(data={ATTR_ENDPOINT: "MadMapper"})

    assert integration._resolve_endpoint(hass, call) is hass.data[DOMAIN]["entry-1"]


def test_endpoint_config_uses_target_setting_options() -> None:
    entry = SimpleNamespace(
        entry_id="entry-1",
        data={
            CONF_NAME: "Original",
            CONF_REMOTE_HOST: "192.0.2.10",
            CONF_REMOTE_PORT: 9000,
            CONF_RECEIVE_ENABLED: True,
            CONF_LOCAL_BIND_ADDRESS: "0.0.0.0",
            CONF_LOCAL_PORT: 9001,
            CONF_ALLOWED_SOURCE_IPS: [],
        },
        options={
            CONF_NAME: "MadMapper",
            CONF_REMOTE_HOST: "192.0.2.20",
            CONF_REMOTE_PORT: 8000,
            CONF_RECEIVE_ENABLED: False,
            CONF_LOCAL_BIND_ADDRESS: "127.0.0.1",
            CONF_LOCAL_PORT: 8001,
            CONF_ALLOWED_SOURCE_IPS: ["192.0.2.30"],
        },
    )

    config = integration._endpoint_config_from_entry(entry)

    assert config.name == "MadMapper"
    assert config.remote_host == "192.0.2.20"
    assert config.remote_port == 8000
    assert config.receive_enabled is False
    assert config.local_bind_address == "127.0.0.1"
    assert config.local_port == 8001
    assert config.allowed_source_ips == ["192.0.2.30"]
