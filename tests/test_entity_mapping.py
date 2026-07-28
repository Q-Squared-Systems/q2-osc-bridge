from __future__ import annotations

from types import SimpleNamespace

import pytest

from custom_components.q2_osc_bridge.const import CONF_MAPPINGS
from custom_components.q2_osc_bridge.entity_mapping import (
    OscEntityMapping,
    create_button_mapping,
    mappings_from_entry,
)


def test_mapping_round_trip_through_config_entry_options() -> None:
    mapping = OscEntityMapping(
        platform="number",
        key="dimmer",
        name="Dimmer",
        send_address="/dimmer",
        receive_address="/dimmer/state",
        min_value=0,
        max_value=1,
        step=0.01,
    )
    entry = SimpleNamespace(options={CONF_MAPPINGS: [mapping.as_dict()]})

    assert mappings_from_entry(entry) == [mapping]


def test_mapping_defaults_to_empty_list() -> None:
    assert mappings_from_entry(SimpleNamespace(options={})) == []


def test_options_flow_creates_button_mapping_from_target_path() -> None:
    mapping = create_button_mapping("Channel On", "/channel/1/on")

    assert mapping.platform == "button"
    assert mapping.name == "Channel On"
    assert mapping.send_address == "/channel/1/on"
    assert mapping.receive_address is None


def test_button_mapping_requires_target_path() -> None:
    with pytest.raises(ValueError):
        create_button_mapping("Channel On", "channel/1/on")
