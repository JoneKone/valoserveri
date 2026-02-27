"""Application state for per-light controls."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LightState:
    index: int
    base_rgb: tuple[int, int, int] = (255, 255, 255)
    intensity: int = 255


@dataclass
class AppSettings:
    server_ip: str = "127.0.0.1"
    server_port: int = 9909
    tag: str = "ui-controller"
    num_lights: int = 24


@dataclass
class AppState:
    settings: AppSettings = field(default_factory=AppSettings)
    lights: list[LightState] = field(default_factory=list)

    def ensure_lights(self) -> None:
        n = max(1, min(64, int(self.settings.num_lights)))
        if len(self.lights) == n:
            return

        previous = {l.index: l for l in self.lights}
        self.lights = []
        for i in range(n):
            self.lights.append(previous.get(i, LightState(index=i)))
