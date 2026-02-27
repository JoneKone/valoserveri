"""UDP sender for valoserveri protocol."""

from __future__ import annotations

import socket

from .model import AppState
from .protocol import LightCommand, build_packet, scaled_rgb


class UdpLightClient:
    def __init__(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_state(self, state: AppState) -> None:
        commands: list[LightCommand] = []
        for light in state.lights:
            r, g, b = scaled_rgb(light.base_rgb, light.intensity)
            commands.append(LightCommand(light.index, r, g, b))

        packet = build_packet(state.settings.tag, commands)
        self._socket.sendto(packet, (state.settings.server_ip, int(state.settings.server_port)))
