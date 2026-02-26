import time

import interception

from config import Config
from detector import NoteDetector, NoteKind


class NoteHitter:
    """Traduit une détection en frappe clavier."""

    def __init__(self, config: Config, detector: NoteDetector):
        self.config = config
        self.detector = detector

    def hit(self, key: str, kind: NoteKind, col_x: float):
        if kind == "yellow":
            interception.press(key.lower())
        elif kind == "purple":
            interception.key_down(key.lower())
            while self.detector.is_present(col_x):
                time.sleep(self.config.hold_check_interval)
            interception.key_up(key.lower())
