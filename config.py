from dataclasses import dataclass, field

import numpy as np


@dataclass
class Config:
    # X center of each lane in screen pixels. Adjust until green overlay lines are centered on the game lanes.
    columns: dict[str, float] = field(
        default_factory=lambda: {
            "Q": 418.5,
            "S": 634.5,
            "D": 851.5,
            "J": 1067.5,
            "K": 1284.5,
            "L": 1500.5,
        }
    )

    # Y coordinate (screen pixels) of the hit line — where notes land/disappear. Align red overlay line here.
    hit_line_y: int = 920
    # Y coordinate of the top of the capture zone. Should be above all notes.
    top_y: int = 60
    # Y coordinate where notes are scanned. Should be clearly above hit_line_y with notes fully visible.
    detect_y: int = 850

    # How fast notes fall in pixels/second. hit_delay = (hit_line_y - detect_y) / speed.
    # BIGGER = notes assumed to fall faster = shorter wait before pressing = press EARLIER.
    # SMALLER = notes assumed to fall slower = longer wait before pressing = press LATER.
    # If pressing too early: decrease speed. If pressing too late: increase speed.
    speed: float = 660.0

    # RGB color of tap notes (yellow). Sample with debug_colors.py if detection fails.
    yellow: np.ndarray = field(default_factory=lambda: np.array([253, 176, 85]))
    # RGB color of hold notes (purple). Sample with debug_colors.py if detection fails.
    purple: np.ndarray = field(default_factory=lambda: np.array([165, 138, 255]))
    # How close a pixel's color must be to yellow/purple to count as a note (lower = stricter).
    tolerance: float = 30.0
    # Same threshold but for detecting if a hold note is still active (can be looser).
    hold_tolerance: float = 60.0

    # Minimum seconds between hits on the same column — prevents double-triggering the same note.
    cooldown: float = 0.1
    # Seconds between screen captures (~0.008 = 125 FPS). Lower = more responsive but more CPU.
    capture_interval: float = 0.008
    # Seconds between detection checks per column. Lower = reacts faster but more CPU.
    watch_interval: float = 0.008
    # Seconds between checks for whether a hold note is still active.
    hold_check_interval: float = 0.016

    @property
    def hit_delay(self) -> float:
        # Seconds to wait after detecting a note before pressing the key.
        return (self.hit_line_y - self.detect_y) / self.speed

    @property
    def col_xs(self) -> list[float]:
        return list(self.columns.values())

    @property
    def zone_left(self) -> int:
        return int(min(self.col_xs)) - 10

    @property
    def zone_top(self) -> int:
        return self.top_y

    @property
    def zone_width(self) -> int:
        return int(max(self.col_xs)) - int(min(self.col_xs)) + 20

    @property
    def zone_height(self) -> int:
        return self.hit_line_y - self.top_y
