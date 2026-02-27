"""Tkinter UI for controlling lights over UDP."""

from __future__ import annotations

import tkinter as tk
from tkinter import colorchooser, messagebox, ttk

from .client import UdpLightClient
from .model import AppState


class LightControlUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Valoserveri UDP Light Controller")

        self.state = AppState()
        self.state.ensure_lights()
        self.client = UdpLightClient()

        self._send_after_id: str | None = None
        self.status_var = tk.StringVar(value="Ready")

        self.server_ip_var = tk.StringVar(value=self.state.settings.server_ip)
        self.port_var = tk.StringVar(value=str(self.state.settings.server_port))
        self.tag_var = tk.StringVar(value=self.state.settings.tag)
        self.num_lights_var = tk.StringVar(value=str(self.state.settings.num_lights))

        self._build_layout()
        self._render_light_controls()

    def _build_layout(self) -> None:
        settings = ttk.LabelFrame(self.root, text="Server settings")
        settings.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(settings, text="Server IP").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ttk.Entry(settings, textvariable=self.server_ip_var, width=16).grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(settings, text="UDP Port").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        ttk.Entry(settings, textvariable=self.port_var, width=8).grid(row=0, column=3, padx=6, pady=6, sticky="w")

        ttk.Label(settings, text="Tag").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        ttk.Entry(settings, textvariable=self.tag_var, width=14).grid(row=0, column=5, padx=6, pady=6, sticky="w")

        ttk.Label(settings, text="Number of lights").grid(row=0, column=6, padx=6, pady=6, sticky="w")
        ttk.Entry(settings, textvariable=self.num_lights_var, width=6).grid(row=0, column=7, padx=6, pady=6, sticky="w")

        ttk.Button(settings, text="Apply", command=self.apply_settings).grid(row=0, column=8, padx=6, pady=6)
        ttk.Button(settings, text="Send now", command=self.send_now).grid(row=0, column=9, padx=6, pady=6)

        self.controls_frame = ttk.LabelFrame(self.root, text="Lights")
        self.controls_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        ttk.Label(self.root, textvariable=self.status_var).pack(fill=tk.X, padx=10, pady=(0, 10))

    def apply_settings(self) -> None:
        try:
            num_lights = int(self.num_lights_var.get())
            port = int(self.port_var.get())
        except ValueError:
            messagebox.showerror("Invalid settings", "Port and number of lights must be integers.")
            return

        if num_lights < 1 or num_lights > 64:
            messagebox.showerror("Invalid settings", "Number of lights must be between 1 and 64.")
            return

        self.state.settings.server_ip = self.server_ip_var.get().strip() or "127.0.0.1"
        self.state.settings.server_port = port
        self.state.settings.tag = self.tag_var.get().strip() or "ui-controller"
        self.state.settings.num_lights = num_lights
        self.state.ensure_lights()
        self._render_light_controls()
        self.status_var.set(f"Settings updated ({num_lights} lights)")

    def _render_light_controls(self) -> None:
        for child in self.controls_frame.winfo_children():
            child.destroy()

        max_columns = 6
        for light in self.state.lights:
            col = light.index % max_columns
            row = light.index // max_columns

            frame = ttk.Frame(self.controls_frame, padding=6)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="n")

            ttk.Label(frame, text=f"Light {light.index}").pack()

            color_button = tk.Button(
                frame,
                text="RGB",
                width=8,
                bg=self._rgb_to_hex(light.base_rgb),
                fg="white",
                command=lambda idx=light.index: self.choose_color(idx),
            )
            color_button.pack(pady=(2, 6))

            slider = ttk.Scale(
                frame,
                from_=0,
                to=255,
                orient=tk.VERTICAL,
                length=140,
                command=lambda value, idx=light.index: self.on_intensity_changed(idx, value),
            )
            slider.set(light.intensity)
            slider.pack()

            value_lbl = ttk.Label(frame, text=f"{light.intensity:3d}")
            value_lbl.pack(pady=(4, 0))

            slider.configure(command=lambda value, idx=light.index, lbl=value_lbl: self.on_intensity_changed(idx, value, lbl))

    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        r, g, b = rgb
        return f"#{r:02x}{g:02x}{b:02x}"

    def choose_color(self, index: int) -> None:
        light = self.state.lights[index]
        _, hex_color = colorchooser.askcolor(color=self._rgb_to_hex(light.base_rgb), title=f"Select color for light {index}")
        if not hex_color:
            return

        light.base_rgb = (
            int(hex_color[1:3], 16),
            int(hex_color[3:5], 16),
            int(hex_color[5:7], 16),
        )
        self._render_light_controls()
        self.queue_send("Color updated")

    def on_intensity_changed(self, index: int, value: str, label: ttk.Label | None = None) -> None:
        intensity = int(float(value))
        self.state.lights[index].intensity = intensity
        if label is not None:
            label.config(text=f"{intensity:3d}")
        self.queue_send("Intensity changed")

    def queue_send(self, reason: str) -> None:
        if self._send_after_id is not None:
            self.root.after_cancel(self._send_after_id)
        self._send_after_id = self.root.after(80, lambda: self._send(reason))

    def send_now(self) -> None:
        self._send("Manual send")

    def _send(self, reason: str) -> None:
        self._send_after_id = None
        try:
            self.client.send_state(self.state)
            self.status_var.set(f"{reason}: sent {len(self.state.lights)} lights to {self.state.settings.server_ip}:{self.state.settings.server_port}")
        except OSError as exc:
            self.status_var.set(f"Send failed: {exc}")
