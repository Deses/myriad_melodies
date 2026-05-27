import signal

import win32con
import win32gui

from bot import RhythmBot
from config import Config
from overlay import Overlay
from resolution import find_genshin_hwnd


def _activate_game():
    hwnd = find_genshin_hwnd()
    if not hwnd:
        print("[WARN] Genshin Impact window not found - is the game running?")
        return
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        print("[INFO] Genshin Impact window activated")
    except Exception as e:
        print(f"[WARN] Could not activate game window: {e}")


if __name__ == "__main__":
    config = Config()
    bot = RhythmBot(config)
    overlay = Overlay(config, bot)

    signal.signal(signal.SIGINT, lambda *_: overlay.root.after(0, overlay.quit))

    _activate_game()
    try:
        bot.start()
        overlay.run()
    except KeyboardInterrupt:
        print("\n[main] stopping...")
    finally:
        bot.stop()
        print("[main] done")
