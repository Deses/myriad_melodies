# Myriad Melodies Bot

Automatic detection and input bot for the Myriad Melodies rhythm mini-game in Genshin Impact.
Captures the screen in real time, detects notes by color, and simulates keystrokes via Win32 SendInput.

## Requirements

- Windows
- Python 3.10+

No kernel drivers needed.

## Installation

Double-click `run.bat` - it will auto-elevate to administrator, create the virtual environment, install dependencies, and launch the bot.

On subsequent runs it skips the install step.

## Usage

Launch Genshin Impact in **borderless windowed** mode, then double-click `run.bat`.

The bot finds the game window automatically by process name (`GenshinImpact.exe`) and brings it to the foreground.

The overlay draws:
- Green vertical lines - monitored lane positions
- Red horizontal line - hit line
- Cyan horizontal line - detection line (where notes are scanned)

To stop: press `F8`, press `Escape`, or click the **[X] Quit** button on the overlay.

Supported resolutions: 1920x1080, 1920x1200, 2560x1080 (UWFHD), 2560x1440 (QHD), 3440x1440 (UWQHD).
Unknown resolutions fall back to proportional scaling from 1080p with a warning.

If the wrong resolution profile is loaded, set `FORCE_RESOLUTION` at the top of `resolution.py`.

## Configuration

All tuning parameters are in `config.py`:

| Parameter | Default | Description |
|---|---|---|
| `speed` | `660.0` | Assumed note fall speed in px/s. Controls how early keys are pressed. Higher = press earlier, lower = press later. |
| `detect_y` | profile-dependent | Y coordinate where notes are scanned (set by resolution profile). |
| `cooldown` | `0.1` | Minimum seconds between hits on the same column. |
| `tolerance` | `30.0` | Color match threshold for note detection (lower = stricter). |
| `hold_tolerance` | `60.0` | Color match threshold for detecting if a hold note is still active. |
| `capture_interval` | `0.008` | Seconds between screen captures (~125 FPS). |

## Dependencies

```
pydirectinput
mss
numpy
pywin32
```
