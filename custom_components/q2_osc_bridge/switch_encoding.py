"""OSC switch encoding helpers."""

from __future__ import annotations


def osc_switch_value(is_on: bool, osc_type: str | None) -> bool | int | float:
    """Return the outgoing OSC value for a switch state."""
    if osc_type == "i:1/0":
        return 1 if is_on else 0
    if osc_type == "i:0/1":
        return 0 if is_on else 1
    if osc_type == "f:1/0":
        return 1.0 if is_on else 0.0
    if osc_type == "f:0/1":
        return 0.0 if is_on else 1.0
    return is_on


def as_bool(value: object, osc_type: str | None = None) -> bool:
    """Coerce an incoming OSC value to a Home Assistant switch state."""
    if osc_type in {"i:0/1", "f:0/1"}:
        return not as_bool(value)
    if isinstance(value, str):
        return value.strip().casefold() not in {"", "0", "false", "off", "no"}
    return bool(value)
