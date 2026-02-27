"""UDP packet protocol helpers for valoserveri light control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class LightCommand:
    index: int
    red: int
    green: int
    blue: int


def _clamp_byte(value: int) -> int:
    return max(0, min(255, int(value)))


def build_packet(tag: str, commands: Sequence[LightCommand]) -> bytes:
    """Build a UDP packet using effectserver protocol version 1."""
    payload = bytearray([1, 0])
    payload.extend(tag.encode("ascii", errors="ignore"))
    payload.append(0)

    for command in commands:
        payload.extend(
            [
                1,
                _clamp_byte(command.index),
                0,
                _clamp_byte(command.red),
                _clamp_byte(command.green),
                _clamp_byte(command.blue),
            ]
        )

    return bytes(payload)


def scaled_rgb(rgb: Iterable[int], intensity: int) -> tuple[int, int, int]:
    """Apply intensity (0..255) to an RGB tuple."""
    scale = _clamp_byte(intensity) / 255.0
    r, g, b = (int(c) for c in rgb)
    return (
        _clamp_byte(round(r * scale)),
        _clamp_byte(round(g * scale)),
        _clamp_byte(round(b * scale)),
    )
