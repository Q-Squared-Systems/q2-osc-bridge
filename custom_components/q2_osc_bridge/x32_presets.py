"""Behringer X32 mapping presets."""

from __future__ import annotations

from collections.abc import Callable

from .entity_mapping import (
    OscEntityMapping,
    create_number_mapping,
    create_switch_mapping,
)


def create_x32_input_channel_mute_mappings() -> list[OscEntityMapping]:
    """Create X32 input channel mute switch mappings."""
    return [
        create_switch_mapping(
            name=f"CH {channel:02d} Mute",
            target_path=f"/ch/{channel:02d}/mix/on",
            source_path=f"/ch/{channel:02d}/mix/on",
            osc_type="i:0/1",
        )
        for channel in range(1, 33)
    ]


def create_x32_input_channel_fader_mappings() -> list[OscEntityMapping]:
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
        for channel in range(1, 33)
    ]


def create_x32_aux_fx_mute_mappings() -> list[OscEntityMapping]:
    """Create X32 aux input and FX return mute switch mappings."""
    return _create_x32_aux_fx_mappings(
        "Mute",
        "on",
        create_switch_mapping,
        "i:0/1",
    )


def create_x32_aux_fx_fader_mappings() -> list[OscEntityMapping]:
    """Create X32 aux input and FX return fader float mappings."""
    return _create_x32_aux_fx_mappings(
        "Fader",
        "fader",
        _create_fader_mapping,
        "f",
    )


def _create_x32_aux_fx_mappings(
    label: str,
    path_suffix: str,
    factory: Callable[..., OscEntityMapping],
    osc_type: str,
) -> list[OscEntityMapping]:
    """Create mappings for the X32 Aux/FX fader bank."""
    return [
        factory(
            name=f"{name} {channel:02d} {label}",
            target_path=f"/{path}/{channel:02d}/mix/{path_suffix}",
            source_path=f"/{path}/{channel:02d}/mix/{path_suffix}",
            osc_type=osc_type,
        )
        for name, path, channels in (
            ("Aux", "auxin", range(1, 9)),
            ("FX", "fxrtn", range(1, 9)),
        )
        for channel in channels
    ]


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
