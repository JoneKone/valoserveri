# light_control_ui

A modular Python Tkinter app for controlling the valoserveri UDP light server.

## Features

- Server settings in UI:
  - Server IP
  - UDP port (default 9909)
  - Sender tag
  - Number of lights
- Individual controls for each light:
  - RGB button opens color picker
  - Vertical intensity slider (0..255)
- Sends one UDP packet containing all light states.

## Run

```bash
python3 -m light_control_ui.app
```

## Protocol used

Packet format follows existing examples (`use_examples/over_udp.py`):

- version byte `1`
- null-terminated tag section (`0 + ascii + 0`)
- repeated commands for each light:
  - `1` (light command type)
  - `index`
  - `0` (extension byte)
  - `R`, `G`, `B`
