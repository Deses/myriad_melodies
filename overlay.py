import ctypes
import tkinter as tk

import win32api
import win32con

from bot import RhythmBot
from config import Config, SCREEN_W, SCREEN_H

QUIT_KEY = win32con.VK_F8

_dpi_scale = ctypes.windll.user32.GetDpiForSystem() / 96.0


def _px(v):
    return int(v / _dpi_scale)


class Overlay:
    REFRESH_MS = 16

    def __init__(self, config: Config, bot: RhythmBot):
        self.config = config
        self.bot = bot
        self._win_w = int(SCREEN_W / _dpi_scale)
        self._win_h = int(SCREEN_H / _dpi_scale)
        print(f"[INFO] DPI scale: {_dpi_scale:.3f}  overlay: {self._win_w}x{self._win_h}")
        self._build_window()

    def _build_window(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.attributes("-alpha", 0.8)
        self.root.geometry(f"{self._win_w}x{self._win_h}+0+0")
        self.canvas = tk.Canvas(
            self.root, width=self._win_w, height=self._win_h, bg="black", highlightthickness=0
        )
        self.canvas.pack()

        btn_quit = tk.Button(
            self.root,
            text="[X] Quit  (F8)",
            command=self.quit,
            bg="#ff4444",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=8,
            pady=4,
        )
        btn_quit.place(x=20, y=20)
        self.root.bind("<Escape>", lambda e: self.quit())

    def quit(self):
        self.root.destroy()

    def _poll_quit_key(self):
        if win32api.GetAsyncKeyState(QUIT_KEY) & 1:
            self.root.after(0, self.quit)
            return
        self.root.after(100, self._poll_quit_key)

    def run(self):
        self._poll_quit_key()
        self._draw()
        self.root.mainloop()

    def _draw(self):
        cfg = self.config
        c = self.canvas
        c.delete("all")

        for key, x in cfg.columns.items():
            c.create_line(_px(x), _px(cfg.top_y), _px(x), _px(cfg.hit_line_y), fill="lime", width=2)
            c.create_text(
                _px(x), _px(cfg.top_y) - 15, text=key, fill="lime", font=("Arial", 14, "bold")
            )

        c.create_line(0, _px(cfg.hit_line_y), self._win_w, _px(cfg.hit_line_y), fill="red", width=2)
        c.create_line(0, _px(cfg.detect_y), self._win_w, _px(cfg.detect_y), fill="cyan", width=1)

        self.root.after(self.REFRESH_MS, self._draw)
