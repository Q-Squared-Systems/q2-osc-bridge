"""Validation and normalization helpers for Q2 OSC Bridge."""

from __future__ import annotations

import ipaddress
from collections.abc import Iterable
from typing import Any

import voluptuous as vol

PORT_SCHEMA = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))


def validate_port(value: Any) -> int:
    """Validate a UDP port."""
    port = int(value)
    if port < 1 or port > 65535:
        raise vol.Invalid("port must be between 1 and 65535")
    return port


def normalize_allowed_source_ips(value: Any) -> list[str]:
    """Normalize a comma-separated string or iterable of source IP addresses."""
    if value in (None, ""):
        return []
    if isinstance(value, str):
        candidates = [item.strip() for item in value.split(",")]
    elif isinstance(value, Iterable):
        candidates = [str(item).strip() for item in value]
    else:
        raise vol.Invalid("allowed source IPs must be a string or list")

    addresses: list[str] = []
    for candidate in candidates:
        if not candidate:
            continue
        try:
            addresses.append(str(ipaddress.ip_address(candidate)))
        except ValueError as err:
            raise vol.Invalid(f"invalid source IP address: {candidate}") from err
    return addresses


def normalize_osc_arguments(value: Any) -> list[Any]:
    """Normalize Home Assistant service data into OSC argument values."""
    if value is None:
        return []
    if isinstance(value, list):
        return [_normalize_osc_argument(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_osc_argument(item) for item in value]
    return [_normalize_osc_argument(value)]


def _normalize_osc_argument(value: Any) -> Any:
    """Normalize one OSC argument to a type supported by python-osc."""
    if isinstance(value, bool | int | float | str | bytes) or value is None:
        return value
    raise vol.Invalid(f"unsupported OSC argument type: {type(value).__name__}")


def validate_osc_address(value: Any) -> str:
    """Validate an OSC address pattern for simple message sending."""
    address = str(value)
    if not address.startswith("/"):
        raise vol.Invalid("OSC address must start with /")
    if not address.strip():
        raise vol.Invalid("OSC address is required")
    return address
