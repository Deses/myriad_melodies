import tkinter as tk

from bot import RhythmBot
from config import Config


class Overlay:
    """Overlay tkinter transparent pour visualiser les zones de détection."""

    REFRESH_MS = 16

    def __init__(self, config: Config, bot: RhythmBot):
        self.config = config
        self.bot = bot
        self._build_window()

    def _build_window(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.attributes("-alpha", 0.8)
        self.root.geometry("1920x1080+0+0")
        self.canvas = tk.Canvas(
            self.root, width=1920, height=1080, bg="black", highlightthickness=0
        )
        self.canvas.pack()

    def run(self):
        self._draw()
        self.root.mainloop()

    def _draw(self):
        cfg = self.config
        c = self.canvas
        c.delete("all")

        for key, x in cfg.columns.items():
            c.create_line(x, cfg.top_y, x, cfg.hit_line_y, fill="lime", width=2)
            c.create_text(
                x, cfg.top_y - 15, text=key, fill="lime", font=("Arial", 14, "bold")
            )

        c.create_line(0, cfg.hit_line_y, 1920, cfg.hit_line_y, fill="red", width=2)
        c.create_line(0, cfg.detect_y, 1920, cfg.detect_y, fill="cyan", width=1)

        self.root.after(self.REFRESH_MS, self._draw)
