import threading
import time

import mss
import numpy as np

from config import Config


class FrameCapture:
    """Capture l'écran en continu dans un thread dédié."""

    def __init__(self, config: Config):
        self.config = config
        self._frame: np.ndarray | None = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    @property
    def frame(self) -> np.ndarray | None:
        with self._lock:
            return self._frame

    def _loop(self):
        cfg = self.config
        zone = {
            "left": cfg.zone_left,
            "top": cfg.zone_top,
            "width": cfg.zone_width,
            "height": cfg.zone_height,
        }
        with mss.mss() as sct:
            while not self._stop_event.is_set():
                raw = np.array(sct.grab(zone))[:, :, :3][:, :, ::-1]
                with self._lock:
                    self._frame = raw
                time.sleep(cfg.capture_interval)
