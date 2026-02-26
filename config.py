from dataclasses import dataclass, field

import numpy as np


@dataclass
class Config:
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

    hit_line_y: int = 920
    top_y: int = 60
    detect_y: int = 850
    speed: float = 660.0

    yellow: np.ndarray = field(default_factory=lambda: np.array([253, 176, 85]))
    purple: np.ndarray = field(default_factory=lambda: np.array([165, 138, 255]))
    tolerance: float = 30.0
    hold_tolerance: float = 60.0

    cooldown: float = 0.1
    capture_interval: float = 0.008
    watch_interval: float = 0.008
    hold_check_interval: float = 0.016

    @property
    def hit_delay(self) -> float:
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
