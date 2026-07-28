"""Persistent OSC entity mapping definitions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .const import CONF_MAPPINGS


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
    min_value: float = 0
    max_value: float = 100
    step: float = 1

    def as_dict(self) -> dict[str, Any]:
        """Return a config-entry-safe representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OscEntityMapping:
        """Build a mapping from config entry options."""
        return cls(
            platform=data["platform"],
            key=data["key"],
            name=data["name"],
            receive_address=data.get("receive_address") or None,
            send_address=data.get("send_address") or None,
            initial_value=data.get("initial_value"),
            options=list(data.get("options", [])),
            min_value=float(data.get("min_value", 0)),
            max_value=float(data.get("max_value", 100)),
            step=float(data.get("step", 1)),
        )


def mappings_from_entry(entry: Any) -> list[OscEntityMapping]:
    """Return configured mappings for a config entry."""
    return [
        OscEntityMapping.from_dict(mapping)
        for mapping in entry.options.get(CONF_MAPPINGS, [])
    ]
