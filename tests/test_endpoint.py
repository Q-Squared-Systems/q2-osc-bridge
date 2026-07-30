from __future__ import annotations

import asyncio
from typing import Any

import pytest

from custom_components.q2_osc_bridge.const import EVENT_OSC_MESSAGE
from custom_components.q2_osc_bridge.endpoint import (
    EndpointConfig,
    Q2OscEndpoint,
    build_osc_message,
    infer_type_tags,
)


def _endpoint_config(**overrides: Any) -> EndpointConfig:
    values = {
        "entry_id": "entry-1",
        "name": "Stage Rack",
        "remote_host": "127.0.0.1",
        "remote_port": 9000,
        "receive_enabled": True,
        "local_bind_address": "127.0.0.1",
        "local_port": 9001,
        "allowed_source_ips": [],
    }
    values.update(overrides)
    return EndpointConfig(**values)


def test_infer_type_tags() -> None:
    assert infer_type_tags([1, 2.5, "go", True, False, None]) == "ifsTFN"


def test_endpoint_emits_event_for_incoming_osc_message() -> None:
    events: list[tuple[str, dict[str, Any]]] = []
    endpoint = Q2OscEndpoint(
        hass=None,
        config=_endpoint_config(),
        event_callback=lambda event_type, event_data: events.append(
            (event_type, event_data)
        ),
    )

    endpoint.handle_datagram(
        build_osc_message("/q2/lift/1/position", [12.5, "ready"]),
        ("192.168.1.50", 53000),
    )

    assert len(events) == 1
    event_type, data = events[0]
    assert event_type == EVENT_OSC_MESSAGE
    assert data["endpoint_id"] == "entry-1"
    assert data["entry_id"] == "entry-1"
    assert data["endpoint_name"] == "Stage Rack"
    assert data["source_ip"] == "192.168.1.50"
    assert data["source_port"] == 53000
    assert data["address"] == "/q2/lift/1/position"
    assert data["arguments"] == [12.5, "ready"]
    assert data["type_tags"] == "fs"
    assert "timestamp" in data
    assert endpoint.diagnostics.received_messages == 1
    assert endpoint.diagnostics.last_source == "192.168.1.50:53000"


def test_endpoint_ignores_disallowed_source_ip() -> None:
    events: list[tuple[str, dict[str, Any]]] = []
    endpoint = Q2OscEndpoint(
        hass=None,
        config=_endpoint_config(allowed_source_ips=["10.0.0.1"]),
        event_callback=lambda event_type, event_data: events.append(
            (event_type, event_data)
        ),
    )

    endpoint.handle_datagram(build_osc_message("/q2/test", [1]), ("10.0.0.2", 53000))

    assert events == []
    assert endpoint.diagnostics.received_messages == 0


def test_endpoint_counts_decode_errors() -> None:
    endpoint = Q2OscEndpoint(
        hass=None,
        config=_endpoint_config(),
        event_callback=lambda event_type, event_data: None,
    )

    endpoint.handle_datagram(b"not osc", ("127.0.0.1", 53000))

    assert endpoint.diagnostics.decode_errors == 1


def test_endpoint_notifies_and_removes_message_listener() -> None:
    messages: list[dict[str, Any]] = []
    endpoint = Q2OscEndpoint(
        hass=None,
        config=_endpoint_config(),
        event_callback=lambda event_type, event_data: None,
    )
    remove_listener = endpoint.add_message_listener(messages.append)

    endpoint.handle_datagram(build_osc_message("/mapped", [7]), ("127.0.0.1", 53000))
    remove_listener()
    endpoint.handle_datagram(build_osc_message("/mapped", [8]), ("127.0.0.1", 53000))

    assert len(messages) == 1
    assert messages[0]["address"] == "/mapped"
    assert messages[0]["arguments"] == [7]


@pytest.mark.asyncio
async def test_endpoint_keepalive_sends_configured_path() -> None:
    endpoint = Q2OscEndpoint(
        hass=None,
        config=_endpoint_config(
            keepalive_enabled=True,
            keepalive_path="/xremote",
            keepalive_interval=60,
        ),
    )
    try:
        await endpoint.async_start()
    except PermissionError:
        pytest.skip("local UDP socket binding is blocked in this environment")

    for _ in range(20):
        if endpoint.diagnostics.keepalive_messages:
            break
        await asyncio.sleep(0)

    await endpoint.async_stop()

    assert endpoint.diagnostics.keepalive_messages == 1
    assert endpoint.diagnostics.sent_messages == 1
    assert endpoint.diagnostics.last_keepalive_time is not None


@pytest.mark.asyncio
async def test_endpoint_stop_releases_udp_port_before_restart() -> None:
    first = Q2OscEndpoint(
        hass=None,
        config=_endpoint_config(local_bind_address="127.0.0.1", local_port=0),
    )
    try:
        await first.async_start()
    except PermissionError:
        pytest.skip("local UDP socket binding is blocked in this environment")
    transport = first._transport
    assert transport is not None
    sock = transport.get_extra_info("socket")
    port = sock.getsockname()[1]

    await first.async_stop()

    second = Q2OscEndpoint(
        hass=None,
        config=_endpoint_config(local_bind_address="127.0.0.1", local_port=port),
    )
    await second.async_start()
    await second.async_stop()
