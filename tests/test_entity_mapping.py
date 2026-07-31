from __future__ import annotations

from types import SimpleNamespace

import pytest

from custom_components.q2_osc_bridge.const import CONF_MAPPINGS
from custom_components.q2_osc_bridge.entity_mapping import (
    OscEntityMapping,
    create_button_mapping,
    create_number_mapping,
    create_sensor_mapping,
    create_switch_mapping,
    create_text_mapping,
    mappings_from_entry,
)
from custom_components.q2_osc_bridge.x32_presets import (
    create_x32_aux_fx_fader_mappings,
    create_x32_aux_fx_mute_mappings,
    create_x32_aux_return_fader_mappings,
    create_x32_aux_return_mute_mappings,
    create_x32_input_channel_fader_mappings,
    create_x32_input_channel_mute_mappings,
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


def test_options_flow_creates_number_mapping_from_target_and_source_paths() -> None:
    mapping = create_number_mapping(
        "Opacity",
        "/layer/1/opacity",
        "/layer/1/opacity/feedback",
        min_value=0,
        max_value=1,
        step=0.01,
    )

    assert mapping.platform == "number"
    assert mapping.name == "Opacity"
    assert mapping.send_address == "/layer/1/opacity"
    assert mapping.receive_address == "/layer/1/opacity/feedback"
    assert mapping.min_value == 0
    assert mapping.max_value == 1
    assert mapping.step == 0.01


def test_number_mapping_rejects_invalid_range() -> None:
    with pytest.raises(ValueError):
        create_number_mapping("Opacity", "/layer/1/opacity", min_value=1, max_value=1)


def test_number_mapping_requires_target_path() -> None:
    with pytest.raises(ValueError):
        create_number_mapping("Opacity", "layer/1/opacity")


def test_options_flow_creates_integer_mapping() -> None:
    mapping = create_number_mapping(
        "Cue Index",
        "/cue/index",
        "/cue/index/feedback",
        min_value=0,
        max_value=255,
        step=1,
        osc_type="i",
    )

    assert mapping.platform == "number"
    assert mapping.osc_type == "i"
    assert mapping.step == 1
    assert mapping.send_address == "/cue/index"
    assert mapping.receive_address == "/cue/index/feedback"


def test_options_flow_creates_boolean_mapping() -> None:
    mapping = create_switch_mapping(
        "Layer Visible", "/layer/1/visible", "/layer/1/visible/feedback"
    )

    assert mapping.platform == "switch"
    assert mapping.osc_type == "T/F"
    assert mapping.send_address == "/layer/1/visible"
    assert mapping.receive_address == "/layer/1/visible/feedback"


def test_boolean_mapping_requires_target_path() -> None:
    with pytest.raises(ValueError):
        create_switch_mapping("Layer Visible", "layer/1/visible")


def test_options_flow_creates_text_mapping() -> None:
    mapping = create_text_mapping("Label", "/layer/1/name", "/layer/1/name/feedback")

    assert mapping.platform == "text"
    assert mapping.osc_type == "s"
    assert mapping.send_address == "/layer/1/name"
    assert mapping.receive_address == "/layer/1/name/feedback"


def test_text_mapping_requires_target_path() -> None:
    with pytest.raises(ValueError):
        create_text_mapping("Label", "layer/1/name")


def test_options_flow_creates_sensor_mapping_from_source_path() -> None:
    mapping = create_sensor_mapping("Layer Opacity", "/layer/1/opacity")

    assert mapping.platform == "sensor"
    assert mapping.name == "Layer Opacity"
    assert mapping.receive_address == "/layer/1/opacity"
    assert mapping.send_address is None


def test_sensor_mapping_requires_source_path() -> None:
    with pytest.raises(ValueError):
        create_sensor_mapping("Layer Opacity", "layer/1/opacity")


def test_x32_input_channel_mute_preset_creates_inverted_integer_switches() -> None:
    mappings = create_x32_input_channel_mute_mappings()

    assert len(mappings) == 32
    assert mappings[0].platform == "switch"
    assert mappings[0].name == "CH 01 Mute"
    assert mappings[0].send_address == "/ch/01/mix/on"
    assert mappings[0].receive_address == "/ch/01/mix/on"
    assert mappings[0].osc_type == "i:0/1"
    assert mappings[-1].name == "CH 32 Mute"
    assert mappings[-1].send_address == "/ch/32/mix/on"


def test_x32_input_channel_mute_preset_can_create_selected_channels() -> None:
    mappings = create_x32_input_channel_mute_mappings([1, 8])

    assert len(mappings) == 2
    assert [mapping.name for mapping in mappings] == ["CH 01 Mute", "CH 08 Mute"]
    assert [mapping.send_address for mapping in mappings] == [
        "/ch/01/mix/on",
        "/ch/08/mix/on",
    ]


def test_x32_input_channel_fader_preset_creates_float_numbers() -> None:
    mappings = create_x32_input_channel_fader_mappings()

    assert len(mappings) == 32
    assert mappings[0].platform == "number"
    assert mappings[0].name == "CH 01 Fader"
    assert mappings[0].send_address == "/ch/01/mix/fader"
    assert mappings[0].receive_address == "/ch/01/mix/fader"
    assert mappings[0].min_value == 0
    assert mappings[0].max_value == 1
    assert mappings[0].step == 0.01
    assert mappings[0].osc_type == "f"
    assert mappings[-1].name == "CH 32 Fader"
    assert mappings[-1].send_address == "/ch/32/mix/fader"


def test_x32_aux_return_mute_preset_creates_inverted_integer_switches() -> None:
    mappings = create_x32_aux_return_mute_mappings()

    assert len(mappings) == 8
    assert mappings[0].platform == "switch"
    assert mappings[0].name == "Aux 01 Mute"
    assert mappings[0].send_address == "/auxin/01/mix/on"
    assert mappings[0].receive_address == "/auxin/01/mix/on"
    assert mappings[0].osc_type == "i:0/1"
    assert mappings[-1].name == "Aux 08 Mute"
    assert mappings[-1].send_address == "/auxin/08/mix/on"


def test_x32_aux_return_fader_preset_creates_float_numbers() -> None:
    mappings = create_x32_aux_return_fader_mappings([1, 8])

    assert len(mappings) == 2
    assert mappings[0].platform == "number"
    assert mappings[0].name == "Aux 01 Fader"
    assert mappings[0].send_address == "/auxin/01/mix/fader"
    assert mappings[0].receive_address == "/auxin/01/mix/fader"
    assert mappings[0].min_value == 0
    assert mappings[0].max_value == 1
    assert mappings[0].step == 0.01
    assert mappings[0].osc_type == "f"
    assert mappings[-1].name == "Aux 08 Fader"
    assert mappings[-1].send_address == "/auxin/08/mix/fader"


def test_x32_aux_fx_mute_preset_creates_inverted_integer_switches() -> None:
    mappings = create_x32_aux_fx_mute_mappings()

    assert len(mappings) == 16
    assert mappings[0].platform == "switch"
    assert mappings[0].name == "Aux 01 Mute"
    assert mappings[0].send_address == "/auxin/01/mix/on"
    assert mappings[0].receive_address == "/auxin/01/mix/on"
    assert mappings[0].osc_type == "i:0/1"
    assert mappings[7].name == "Aux 08 Mute"
    assert mappings[7].send_address == "/auxin/08/mix/on"
    assert mappings[8].name == "FX 01 Mute"
    assert mappings[8].send_address == "/fxrtn/01/mix/on"
    assert mappings[-1].name == "FX 08 Mute"
    assert mappings[-1].send_address == "/fxrtn/08/mix/on"


def test_x32_aux_fx_mute_preset_can_create_selected_banks() -> None:
    mappings = create_x32_aux_fx_mute_mappings(aux_channels=[1, 3], fx_channels=[2])

    assert len(mappings) == 3
    assert [mapping.name for mapping in mappings] == [
        "Aux 01 Mute",
        "Aux 03 Mute",
        "FX 02 Mute",
    ]
    assert [mapping.send_address for mapping in mappings] == [
        "/auxin/01/mix/on",
        "/auxin/03/mix/on",
        "/fxrtn/02/mix/on",
    ]


def test_x32_aux_fx_fader_preset_creates_float_numbers() -> None:
    mappings = create_x32_aux_fx_fader_mappings()

    assert len(mappings) == 16
    assert mappings[0].platform == "number"
    assert mappings[0].name == "Aux 01 Fader"
    assert mappings[0].send_address == "/auxin/01/mix/fader"
    assert mappings[0].receive_address == "/auxin/01/mix/fader"
    assert mappings[0].min_value == 0
    assert mappings[0].max_value == 1
    assert mappings[0].step == 0.01
    assert mappings[0].osc_type == "f"
    assert mappings[7].name == "Aux 08 Fader"
    assert mappings[7].send_address == "/auxin/08/mix/fader"
    assert mappings[8].name == "FX 01 Fader"
    assert mappings[8].send_address == "/fxrtn/01/mix/fader"
    assert mappings[-1].name == "FX 08 Fader"
    assert mappings[-1].send_address == "/fxrtn/08/mix/fader"
