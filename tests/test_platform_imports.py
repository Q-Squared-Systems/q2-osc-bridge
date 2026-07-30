from __future__ import annotations

import importlib
import sys
from types import ModuleType


def _module(name: str) -> ModuleType:
    module = ModuleType(name)
    sys.modules[name] = module
    return module


def test_platform_modules_import_with_homeassistant_stubs() -> None:
    ha = _module("homeassistant")
    components = _module("homeassistant.components")
    ha.components = components

    for platform, entity_class in {
        "binary_sensor": "BinarySensorEntity",
        "button": "ButtonEntity",
        "number": "NumberEntity",
        "select": "SelectEntity",
        "sensor": "SensorEntity",
        "switch": "SwitchEntity",
        "text": "TextEntity",
    }.items():
        module = _module(f"homeassistant.components.{platform}")
        setattr(module, entity_class, type(entity_class, (), {}))
        setattr(components, platform, module)

    config_entries = _module("homeassistant.config_entries")
    config_entries.ConfigEntry = type("ConfigEntry", (), {})
    core = _module("homeassistant.core")
    core.HomeAssistant = type("HomeAssistant", (), {})
    helpers = _module("homeassistant.helpers")
    entity = _module("homeassistant.helpers.entity")
    entity.Entity = type("Entity", (), {})
    entity_platform = _module("homeassistant.helpers.entity_platform")
    entity_platform.AddEntitiesCallback = object
    ha.config_entries = config_entries
    ha.core = core
    ha.helpers = helpers
    helpers.entity = entity
    helpers.entity_platform = entity_platform

    for platform in (
        "binary_sensor",
        "button",
        "number",
        "select",
        "sensor",
        "switch",
        "text",
    ):
        importlib.import_module(f"custom_components.q2_osc_bridge.{platform}")
