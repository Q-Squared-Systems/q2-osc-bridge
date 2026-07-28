"""Async OSC endpoint transport handling."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.osc_packet import OscPacket

from .const import EVENT_OSC_MESSAGE
from .validators import normalize_osc_arguments, validate_osc_address


@dataclass(slots=True)
class EndpointConfig:
    """Runtime configuration for one OSC endpoint."""

    entry_id: str
    name: str
    remote_host: str
    remote_port: int
    receive_enabled: bool
    local_bind_address: str
    local_port: int
    allowed_source_ips: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EndpointDiagnostics:
    """Runtime counters for one OSC endpoint."""

    received_messages: int = 0
    sent_messages: int = 0
    decode_errors: int = 0
    send_errors: int = 0
    last_source: str | None = None
    last_message_time: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable diagnostics payload."""
        return {
            "received_messages": self.received_messages,
            "sent_messages": self.sent_messages,
            "decode_errors": self.decode_errors,
            "send_errors": self.send_errors,
            "last_source": self.last_source,
            "last_message_time": self.last_message_time,
        }


class Q2OscDatagramProtocol(asyncio.DatagramProtocol):
    """Datagram protocol that forwards packets to an endpoint."""

    def __init__(self, endpoint: Q2OscEndpoint) -> None:
        self.endpoint = endpoint
        self._closed = asyncio.get_running_loop().create_future()

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Handle one incoming UDP datagram."""
        self.endpoint.handle_datagram(data, addr)

    def error_received(self, exc: Exception) -> None:
        """Track UDP transport errors."""
        self.endpoint.diagnostics.decode_errors += 1

    def connection_lost(self, exc: Exception | None) -> None:
        """Mark the UDP transport as fully closed."""
        if not self._closed.done():
            self._closed.set_result(None)

    async def async_wait_closed(self) -> None:
        """Wait until asyncio has finished closing the UDP transport."""
        await self._closed


class Q2OscEndpoint:
    """One configured OSC endpoint with one owned UDP transport."""

    def __init__(
        self,
        hass: Any,
        config: EndpointConfig,
        event_callback: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        self.hass = hass
        self.config = config
        self.diagnostics = EndpointDiagnostics()
        self._transport: asyncio.DatagramTransport | None = None
        self._protocol: Q2OscDatagramProtocol | None = None
        self._event_callback = event_callback
        self._message_listeners: set[Callable[[dict[str, Any]], None]] = set()

    @property
    def entry_id(self) -> str:
        """Return the config entry id."""
        return self.config.entry_id

    @property
    def name(self) -> str:
        """Return the endpoint name."""
        return self.config.name

    async def async_start(self) -> None:
        """Bind the UDP transport for this endpoint."""
        loop = self.hass.loop if self.hass is not None else asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: Q2OscDatagramProtocol(self),
            local_addr=(self.config.local_bind_address, self.config.local_port),
        )
        self._transport = transport
        self._protocol = protocol

    async def async_stop(self) -> None:
        """Close the UDP transport."""
        transport = self._transport
        protocol = self._protocol
        self._transport = None
        self._protocol = None

        if transport is not None:
            transport.close()
        if protocol is not None:
            await asyncio.wait_for(protocol.async_wait_closed(), timeout=1)

    def add_message_listener(
        self,
        listener: Callable[[dict[str, Any]], None],
    ) -> Callable[[], None]:
        """Subscribe to decoded OSC messages."""
        self._message_listeners.add(listener)
        return lambda: self._message_listeners.discard(listener)

    async def async_send(self, address: str, arguments: Any = None) -> None:
        """Encode and send an OSC message through this endpoint's transport."""
        if self._transport is None:
            raise RuntimeError("OSC endpoint transport is not started")

        try:
            message = build_osc_message(address, arguments)
            self._transport.sendto(
                message,
                (self.config.remote_host, self.config.remote_port),
            )
            self.diagnostics.sent_messages += 1
        except Exception:
            self.diagnostics.send_errors += 1
            raise

    def handle_datagram(self, data: bytes, addr: tuple[str, int]) -> None:
        """Decode incoming OSC datagrams and emit Home Assistant events."""
        source_ip, source_port = addr
        if not self.config.receive_enabled:
            return
        if (
            self.config.allowed_source_ips
            and source_ip not in self.config.allowed_source_ips
        ):
            return

        try:
            packet = OscPacket(data)
        except Exception:
            self.diagnostics.decode_errors += 1
            return

        now = datetime.now(UTC).isoformat()
        self.diagnostics.last_source = f"{source_ip}:{source_port}"
        self.diagnostics.last_message_time = now

        for timed_message in packet.messages:
            message = timed_message.message
            arguments = list(message.params)
            event_data = {
                "endpoint_id": self.config.entry_id,
                "entry_id": self.config.entry_id,
                "endpoint_name": self.config.name,
                "source_ip": source_ip,
                "source_port": source_port,
                "address": message.address,
                "arguments": arguments,
                "type_tags": infer_type_tags(arguments),
                "timestamp": now,
            }
            self.diagnostics.received_messages += 1
            self._fire_event(event_data)
            for listener in tuple(self._message_listeners):
                listener(event_data)

    def _fire_event(self, event_data: dict[str, Any]) -> None:
        """Fire an event through Home Assistant or the injected test callback."""
        if self._event_callback is not None:
            self._event_callback(EVENT_OSC_MESSAGE, event_data)
            return
        self.hass.bus.async_fire(EVENT_OSC_MESSAGE, event_data)


def build_osc_message(address: str, arguments: Any = None) -> bytes:
    """Build an OSC message datagram."""
    builder = OscMessageBuilder(address=validate_osc_address(address))
    for argument in normalize_osc_arguments(arguments):
        builder.add_arg(argument)
    return builder.build().dgram


def infer_type_tags(arguments: list[Any]) -> str:
    """Infer simple OSC type tags for event payloads."""
    tags = []
    for argument in arguments:
        if isinstance(argument, bool):
            tags.append("T" if argument else "F")
        elif isinstance(argument, int):
            tags.append("i")
        elif isinstance(argument, float):
            tags.append("f")
        elif isinstance(argument, str):
            tags.append("s")
        elif isinstance(argument, bytes):
            tags.append("b")
        elif argument is None:
            tags.append("N")
        else:
            tags.append("?")
    return "".join(tags)
