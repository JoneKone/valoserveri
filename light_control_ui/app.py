"""Entry point for modular UDP light control UI."""

from __future__ import annotations

import tkinter as tk

from .ui import LightControlUI


def main() -> None:
    root = tk.Tk()
    LightControlUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
