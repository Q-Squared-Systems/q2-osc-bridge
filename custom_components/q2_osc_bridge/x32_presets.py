"""Behringer X32 mapping presets."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from .entity_mapping import (
    OscEntityMapping,
    create_number_mapping,
    create_switch_mapping,
)


def create_x32_input_channel_mute_mappings(
    channels: Iterable[int] = range(1, 33),
) -> list[OscEntityMapping]:
    """Create X32 input channel mute switch mappings."""
    return [
        create_switch_mapping(
            name=f"Channel {channel:02d}",
            target_path=f"/ch/{channel:02d}/mix/on",
            source_path=f"/ch/{channel:02d}/mix/on",
            osc_type="i:1/0",
        )
        for channel in channels
    ]


def create_x32_input_channel_fader_mappings(
    channels: Iterable[int] = range(1, 33),
) -> list[OscEntityMapping]:
    """Create X32 input channel fader float mappings."""
    return [
        create_number_mapping(
            name=f"CH {channel:02d} Fader",
            target_path=f"/ch/{channel:02d}/mix/fader",
            source_path=f"/ch/{channel:02d}/mix/fader",
            min_value=0,
            max_value=1,
            step=0.01,
            osc_type="f",
        )
        for channel in channels
    ]


def create_x32_aux_return_mute_mappings(
    channels: Iterable[int] = range(1, 9),
) -> list[OscEntityMapping]:
    """Create X32 aux return mute switch mappings."""
    return _create_x32_bank_mappings(
        "Aux",
        "auxin",
        channels,
        None,
        "on",
        create_switch_mapping,
        "i:1/0",
    )


def create_x32_aux_return_fader_mappings(
    channels: Iterable[int] = range(1, 9),
) -> list[OscEntityMapping]:
    """Create X32 aux return fader float mappings."""
    return _create_x32_bank_mappings(
        "Aux",
        "auxin",
        channels,
        "Fader",
        "fader",
        _create_fader_mapping,
        "f",
    )


def create_x32_aux_fx_mute_mappings(
    aux_channels: Iterable[int] = range(1, 9),
    fx_channels: Iterable[int] = range(1, 9),
) -> list[OscEntityMapping]:
    """Create X32 aux input and FX return mute switch mappings."""
    return _create_x32_aux_fx_mappings(
        None,
        "on",
        create_switch_mapping,
        "i:1/0",
        aux_channels,
        fx_channels,
    )


def create_x32_aux_fx_fader_mappings(
    aux_channels: Iterable[int] = range(1, 9),
    fx_channels: Iterable[int] = range(1, 9),
) -> list[OscEntityMapping]:
    """Create X32 aux input and FX return fader float mappings."""
    return _create_x32_aux_fx_mappings(
        "Fader",
        "fader",
        _create_fader_mapping,
        "f",
        aux_channels,
        fx_channels,
    )


def _create_x32_aux_fx_mappings(
    label: str | None,
    path_suffix: str,
    factory: Callable[..., OscEntityMapping],
    osc_type: str,
    aux_channels: Iterable[int],
    fx_channels: Iterable[int],
) -> list[OscEntityMapping]:
    """Create mappings for the X32 Aux/FX fader bank."""
    mappings: list[OscEntityMapping] = []
    mappings.extend(
        _create_x32_bank_mappings(
            "Aux",
            "auxin",
            aux_channels,
            label,
            path_suffix,
            factory,
            osc_type,
        )
    )
    mappings.extend(
        _create_x32_bank_mappings(
            "FX",
            "fxrtn",
            fx_channels,
            label,
            path_suffix,
            factory,
            osc_type,
        )
    )
    return mappings


def _create_x32_bank_mappings(
    name: str,
    path: str,
    channels: Iterable[int],
    label: str | None,
    path_suffix: str,
    factory: Callable[..., OscEntityMapping],
    osc_type: str,
) -> list[OscEntityMapping]:
    """Create mappings for one X32 fader bank."""
    return [
        factory(
            name=_x32_mapping_name(name, channel, label),
            target_path=f"/{path}/{channel:02d}/mix/{path_suffix}",
            source_path=f"/{path}/{channel:02d}/mix/{path_suffix}",
            osc_type=osc_type,
        )
        for channel in channels
    ]


def _x32_mapping_name(name: str, channel: int, label: str | None) -> str:
    """Return the Home Assistant entity name for an X32 preset mapping."""
    base_name = f"{name} {channel:02d}"
    if label is None:
        return base_name
    return f"{base_name} {label}"


def _create_fader_mapping(
    name: str,
    target_path: str,
    source_path: str,
    osc_type: str,
) -> OscEntityMapping:
    """Create an X32 fader number mapping."""
    return create_number_mapping(
        name=name,
        target_path=target_path,
        source_path=source_path,
        min_value=0,
        max_value=1,
        step=0.01,
        osc_type=osc_type,
    )
