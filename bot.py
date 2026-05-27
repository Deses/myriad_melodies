import threading
import time

from capture import FrameCapture
from config import Config
from detector import NoteDetector
from hitter import NoteHitter


class RhythmBot:

    def __init__(self, config: Config):
        self.config = config
        self.capture = FrameCapture(config)
        self.detector = NoteDetector(config, self.capture)
        self.hitter = NoteHitter(config, self.detector)
        self._stop_event = threading.Event()
        self._last_hit: dict[str, float] = {k: 0.0 for k in config.columns}
        self._threads: list[threading.Thread] = []

    def start(self):
        self.capture.start()
        print("[bot] started capture + watch threads")
        for key, col_x in self.config.columns.items():
            t = threading.Thread(
                target=self._watch_column, args=(key, col_x), daemon=True
            )
            t.start()
            self._threads.append(t)

    def stop(self):
        self._stop_event.set()
        self.capture.stop()

    def _watch_column(self, key: str, col_x: float):
        cfg = self.config
        in_note = False
        ticks = 0
        while not self._stop_event.is_set():
            kind = self.detector.detect(col_x, cfg.detect_y)
            now = time.time()

            ticks += 1
            if ticks % 500 == 0:
                frame = self.capture.frame
                print(f"[{key}] alive | frame={'yes' if frame is not None else 'NO'} | last_detection={kind}")

            if kind and not in_note and (now - self._last_hit[key]) > cfg.cooldown:
                in_note = True
                self._last_hit[key] = now
                print(f"[{key}] HIT {kind}")
                threading.Thread(
                    target=self.hitter.hit, args=(key, kind, col_x), daemon=True
                ).start()
            elif not kind:
                in_note = False

            time.sleep(cfg.watch_interval)
