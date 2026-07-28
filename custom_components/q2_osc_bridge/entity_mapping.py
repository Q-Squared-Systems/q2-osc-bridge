"""Persistent OSC entity mapping definitions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

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


def create_button_mapping(name: str, target_path: str) -> OscEntityMapping:
    """Create a button mapping from user-facing fields."""
    name = name.strip()
    target_path = target_path.strip()

    if not name:
        raise ValueError("button name is required")
    if not target_path:
        raise ValueError("target path is required")
    if not target_path.startswith("/"):
        raise ValueError("target path must start with /")

    return OscEntityMapping(
        platform="button",
        key=uuid4().hex,
        name=name,
        send_address=target_path,
    )


def create_sensor_mapping(name: str, source_path: str) -> OscEntityMapping:
    """Create a sensor mapping from user-facing fields."""
    name = name.strip()
    source_path = source_path.strip()

    if not name:
        raise ValueError("sensor name is required")
    if not source_path:
        raise ValueError("source path is required")
    if not source_path.startswith("/"):
        raise ValueError("source path must start with /")

    return OscEntityMapping(
        platform="sensor",
        key=uuid4().hex,
        name=name,
        receive_address=source_path,
    )


def create_number_mapping(
    name: str,
    target_path: str,
    source_path: str | None = None,
    min_value: float = 0,
    max_value: float = 100,
    step: float = 1,
) -> OscEntityMapping:
    """Create a float number mapping from user-facing fields."""
    name = name.strip()
    target_path = target_path.strip()
    source_path = source_path.strip() if source_path else None

    if not name:
        raise ValueError("float control name is required")
    if not target_path:
        raise ValueError("target path is required")
    if not target_path.startswith("/"):
        raise ValueError("target path must start with /")
    if source_path and not source_path.startswith("/"):
        raise ValueError("source path must start with /")
    if min_value >= max_value:
        raise ValueError("minimum must be less than maximum")
    if step <= 0:
        raise ValueError("step must be positive")

    return OscEntityMapping(
        platform="number",
        key=uuid4().hex,
        name=name,
        send_address=target_path,
        receive_address=source_path,
        min_value=min_value,
        max_value=max_value,
        step=step,
    )
