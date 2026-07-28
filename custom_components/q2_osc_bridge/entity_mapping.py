"""Entity mapping scaffolding for Q2 OSC Bridge."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OscEntityMapping:
    """Declarative mapping between Home Assistant entities and OSC messages."""

    platform: str
    key: str
    name: str
    receive_address: str | None = None
    send_address: str | None = None
    initial_value: Any = None
    options: list[str] = field(default_factory=list)


def default_mappings(endpoint_name: str) -> list[OscEntityMapping]:
    """Return initial placeholder mappings for a new endpoint."""
    return [
        OscEntityMapping("sensor", "last_message", f"{endpoint_name} Last Message"),
        OscEntityMapping("binary_sensor", "receiving", f"{endpoint_name} Receiving"),
        OscEntityMapping("button", "ping", f"{endpoint_name} Ping", send_address="/ping"),
        OscEntityMapping("switch", "enabled", f"{endpoint_name} Enabled"),
        OscEntityMapping("number", "value", f"{endpoint_name} Value"),
        OscEntityMapping("select", "mode", f"{endpoint_name} Mode", options=[]),
    ]
