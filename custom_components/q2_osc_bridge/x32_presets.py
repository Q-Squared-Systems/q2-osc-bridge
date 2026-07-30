"""Behringer X32 mapping presets."""

from __future__ import annotations

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
