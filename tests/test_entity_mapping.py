from __future__ import annotations

from types import SimpleNamespace

from custom_components.q2_osc_bridge.const import CONF_MAPPINGS
from custom_components.q2_osc_bridge.entity_mapping import (
    OscEntityMapping,
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
