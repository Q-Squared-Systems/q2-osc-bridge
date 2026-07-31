from __future__ import annotations

from custom_components.q2_osc_bridge.switch_encoding import as_bool, osc_switch_value


def test_x32_mute_switch_uses_standard_integer_encoding() -> None:
    assert osc_switch_value(True, "i:1/0") == 1
    assert osc_switch_value(False, "i:1/0") == 0
    assert as_bool(1, "i:1/0") is True
    assert as_bool(0, "i:1/0") is False


def test_inverted_integer_encoding_remains_available() -> None:
    assert osc_switch_value(True, "i:0/1") == 0
    assert osc_switch_value(False, "i:0/1") == 1
    assert as_bool(0, "i:0/1") is True
    assert as_bool(1, "i:0/1") is False


def test_default_switch_uses_osc_booleans() -> None:
    assert osc_switch_value(True, "T/F") is True
    assert osc_switch_value(False, "T/F") is False
