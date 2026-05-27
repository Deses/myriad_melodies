# Myriad Melodies Bot

Automatic detection and input bot for the Myriad Melodies rhythm mini-game in Genshin Impact.
Captures the screen in real time, detects notes by color, and simulates keystrokes via the Interception kernel driver.

## Requirements

- Windows
- Python 3.10+
- [Interception driver](https://github.com/oblitum/Interception) installed as administrator (reboot required)

## Installation

Double-click `run.bat` - it will create the virtual environment, install dependencies, and launch the bot automatically.

> The script must be run as administrator for the Interception driver to work correctly.

## Usage

Launch Genshin Impact in **borderless windowed** mode, then double-click `run.bat`.

The overlay draws the monitored columns (green lines) and the detection line (cyan line).
Press `Escape` or click **[X] Quit** to stop the bot cleanly.

Supported resolutions: 1920x1080, 1920x1200, 2560x1080 (UWFHD), 2560x1440 (QHD), 3440x1440 (UWQHD).
Unknown resolutions fall back to proportional scaling from 1080p with a warning.

## Configuration

Key parameters at the top of `main.py`:

| Parameter | Default | Description |
|---|---|---|
| `DETECT_Y` | profile-dependent | Y coordinate where notes are scanned |
| `COOLDOWN` | `0.12` | Minimum seconds between hits on the same column |
| `TOLERANCE` | `30` | Color match threshold (lower = stricter) |
| `CONFIRM_FRAMES` | `6` | Consecutive frames without a note before releasing a hold |

## Dependencies

```
interception-python
mss
numpy
opencv-python
pywin32
```
