import time

import pydirectinput

from config import Config
from detector import NoteDetector, NoteKind


class NoteHitter:
    """Traduit une détection en frappe clavier."""

    def __init__(self, config: Config, detector: NoteDetector):
        self.config = config
        self.detector = detector

    def hit(self, key: str, kind: NoteKind, col_x: float):
        time.sleep(self.config.hit_delay)
        if kind == "yellow":
            pydirectinput.press(key.lower())
        elif kind == "purple":
            pydirectinput.keyDown(key.lower())
            while self.detector.is_present(col_x):
                time.sleep(self.config.hold_check_interval)
            pydirectinput.keyUp(key.lower())
