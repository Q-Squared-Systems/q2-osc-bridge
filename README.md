# Q2 OSC Bridge

Q2 OSC Bridge is a Home Assistant custom integration for sending and receiving
Open Sound Control (OSC) messages directly inside Home Assistant Core. It is
designed for HAOS and HACS distribution, and it runs as a normal custom
integration rather than as a Home Assistant add-on or external service.

## Status

This is an initial working integration. It includes endpoint setup, asyncio UDP
transport ownership, OSC send/receive handling through `python-osc`, Home
Assistant event emission, diagnostics counters, HACS metadata, and configurable
OSC entity mappings.

## Installation

### HACS custom repository

1. In HACS, add this repository as a custom repository.
2. Choose category `Integration`.
3. Install **Q2 OSC Bridge**.
4. Restart Home Assistant.
5. Add the integration from **Settings > Devices & services**.

### Manual install

Copy `custom_components/q2_osc_bridge` into your Home Assistant
`custom_components` directory, then restart Home Assistant.

## HAOS compatibility

Q2 OSC Bridge runs inside Home Assistant Core on HAOS. It does not require a
separate container, supervisor add-on, daemon, or host-level service. UDP ports
must be reachable from the HAOS network environment, and any firewall or VLAN
rules between Home Assistant and OSC devices must allow the configured ports.

## Endpoint options

Each configured OSC endpoint supports:

- Name
- Remote host
- Remote port
- Receive enabled
- Local bind address, default `0.0.0.0`
- Local UDP receive port
- Optional allowed source IPs

The integration prefers one bound UDP transport per endpoint. That transport is
used to receive OSC datagrams and to send OSC datagrams to the endpoint's
configured remote host and port.

## Sending OSC

The integration registers the action:

```yaml
action: q2_osc_bridge.send
data:
  endpoint: "Stage Rack"
  address: "/q2/lift/1/target"
  arguments:
    - 42
    - true
```

You can also target a specific config entry:

```yaml
action: q2_osc_bridge.send
data:
  config_entry_id: "01J..."
  address: "/q2/lift/1/enable"
  arguments:
    - true
```

Arguments may be a single scalar value, a list of values, or omitted.

## Entity mappings

Open **Settings > Devices & services > Q2 OSC Bridge**, select **Configure** on
an endpoint, then choose one mapping action. Reopen Configure for each
additional mapping.

**Add button control** creates a Home Assistant `button` entity. Give it a
button name and a target path such as `/layer/1/visible`; pressing the entity
sends that OSC message with no arguments.

**Add sensor monitor** creates a Home Assistant `sensor` entity. Give it a
sensor name and a source path such as `/layer/1/opacity`; when the endpoint
receives an OSC message at that path, the sensor state updates to the first OSC
argument.

OSC formally calls these addresses or address patterns, but Q2 OSC Bridge labels
them as paths in the UI because that is how slash-prefixed OSC controls are
usually read.

The integration internals already have scaffolding for richer mapping types:

- `number` sends and receives numeric values and supports minimum, maximum, and
  step settings.
- `switch` sends `1` for on and `0` for off; received booleans, numbers, and
  common boolean strings update its state.
- `button` sends a message with no arguments and requires a target path.
- `sensor` exposes the first argument received at its source path.
- `binary_sensor` converts the first received argument to an on/off state.
- `select` sends and receives option strings and requires comma-separated
  options.

Changes reload the endpoint automatically. The Configure menu also provides
**Remove entity mapping** when at least one mapping exists.

## Receive events

Incoming OSC messages produce a Home Assistant event named
`q2_osc_bridge_message`.

Example event data:

```json
{
  "endpoint_id": "01J...",
  "entry_id": "01J...",
  "endpoint_name": "Stage Rack",
  "source_ip": "192.168.1.50",
  "source_port": 9001,
  "address": "/q2/lift/1/position",
  "arguments": [12.5],
  "type_tags": "f",
  "timestamp": "2026-07-27T19:30:00.000000+00:00"
}
```

## Diagnostics

The diagnostics payload includes endpoint configuration with sensitive values
redacted where appropriate, plus counters for:

- Received messages
- Sent messages
- Decode errors
- Send errors
- Last source
- Last message time

## Development

Install test dependencies and run:

```bash
python -m pytest
```

Roadmap:

- Add editing for existing entity mappings.
- Add endpoint network settings to the options flow.
- Add import/export for mapping presets.
- Add value transforms, availability rules, and restore behavior.
- Add richer OSC bundle handling and timestamp preservation.
- Add repair flows for unavailable bind ports.
- Expand Home Assistant integration tests with `pytest-homeassistant-custom-component`.
