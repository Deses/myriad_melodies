from typing import Literal

import numpy as np

from capture import FrameCapture
from config import Config

NoteKind = Literal["yellow", "purple"] | None


class NoteDetector:
    """Détecte la couleur des notes dans le frame courant."""

    def __init__(self, config: Config, capture: FrameCapture):
        self.config = config
        self.capture = capture

    def _col_offset(self, col_x: float) -> int:
        return int(col_x) - self.config.zone_left

    def _patch(
        self, col_x: float, target_y: int, window: int = 20
    ) -> np.ndarray | None:
        frame = self.capture.frame
        if frame is None:
            return None
        ox = self._col_offset(col_x)
        oy = target_y - self.config.top_y
        x1, x2 = max(0, ox - 2), min(frame.shape[1], ox + 2)
        y1, y2 = max(0, oy - window), min(frame.shape[0], oy + window)
        patch = frame[y1:y2, x1:x2]
        return patch if patch.size > 0 else None

    def detect(self, col_x: float, target_y: int) -> NoteKind:
        patch = self._patch(col_x, target_y)
        if patch is None:
            return None
        cfg = self.config
        diff_y = np.abs(patch.astype(int) - cfg.yellow).mean(axis=2).min()
        diff_p = np.abs(patch.astype(int) - cfg.purple).mean(axis=2).min()
        if diff_y < cfg.tolerance and diff_y < diff_p:
            return "yellow"
        if diff_p < cfg.tolerance:
            return "purple"
        return None

    def is_present(self, col_x: float) -> bool:
        """Vérifie si une note (longue) est encore visible sur toute la colonne."""
        frame = self.capture.frame
        if frame is None:
            return False
        ox = self._col_offset(col_x)
        x1, x2 = max(0, ox - 2), min(frame.shape[1], ox + 2)
        patch = frame[:, x1:x2]
        diff = np.abs(patch.astype(int) - self.config.purple).mean(axis=2)
        return diff.min() < self.config.hold_tolerance
