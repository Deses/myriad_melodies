import signal
import threading
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor

import pydirectinput
import mss
import numpy as np
import ctypes
import win32api
import win32con
import win32gui
import win32process

# ---------------------------------------------------------------------------
# Resolution detection
# ---------------------------------------------------------------------------

_REF_W, _REF_H = 1920, 1080
_REF_COLUMNS = {"Q": 418.5, "S": 634.5, "D": 851.5, "J": 1067.5, "K": 1284.5, "L": 1500.5}
_REF_HIT_LINE_Y = 920
_REF_TOP_Y = 60
_REF_DETECT_Y = 850

# Add entries here when you calibrate a new resolution manually.
# Proportional scaling is used as fallback for unknown resolutions.
_PROFILES = {
    (1920, 1080): {
        "columns": _REF_COLUMNS,
        "hit_line_y": _REF_HIT_LINE_Y,
        "top_y": _REF_TOP_Y,
        "detect_y": _REF_DETECT_Y,
    },
    # UWQHD: extracted from screenshot. Column X may be off by up to 30px - verify with overlay.
    (3440, 1440): {
        "columns": {"Q": 998.0, "S": 1287.0, "D": 1575.0, "J": 1864.0, "K": 2153.0, "L": 2441.0},
        "hit_line_y": 1227,
        "top_y": 100,
        "detect_y": 1130,
    },
    # 1920x1200: same X as 1080p (same screen width), Y proportionally scaled by 1200/1080.
    (1920, 1200): {
        "columns": {"Q": 418.5, "S": 634.5, "D": 851.5, "J": 1067.5, "K": 1284.5, "L": 1500.5},
        "hit_line_y": 1022,
        "top_y": 67,
        "detect_y": 944,
    },
    # QHD: extracted from screenshot. X may be off up to ~25px - verify with overlay.
    (2560, 1440): {
        "columns": {"Q": 406.0, "S": 614.0, "D": 826.0, "J": 1037.0, "K": 1248.0, "L": 1458.0},
        "hit_line_y": 894,
        "top_y": 60,
        "detect_y": 822,
    },
    # UWFHD: UI scaled to ~78% of 1080p with x_offset=253, y_offset=0. Extracted from screenshot.
    (2560, 1080): {
        "columns": {"Q": 580.0, "S": 747.0, "D": 915.0, "J": 1084.0, "K": 1253.0, "L": 1425.0},
        "hit_line_y": 720,
        "top_y": 47,
        "detect_y": 665,
    },
}


def _scale_profile(sw, sh):
    sx, sy = sw / _REF_W, sh / _REF_H
    return {
        "columns": {k: round(v * sx, 1) for k, v in _REF_COLUMNS.items()},
        "hit_line_y": int(_REF_HIT_LINE_Y * sy),
        "top_y": int(_REF_TOP_Y * sy),
        "detect_y": int(_REF_DETECT_Y * sy),
    }


# Override automatic resolution detection. Set to e.g. (3440, 1440) if detection picks wrong profile.
FORCE_RESOLUTION = None


def _find_genshin_hwnd():
    candidates = []
    def _cb(h, _):
        if not win32gui.IsWindowVisible(h):
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(h)
            hp = win32api.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
            exe = win32process.GetModuleFileNameEx(hp, 0)
            win32api.CloseHandle(hp)
            if "GenshinImpact.exe" in exe:
                candidates.append((h, exe))
        except Exception:
            pass
    win32gui.EnumWindows(_cb, None)
    if candidates:
        h, exe = candidates[0]
        print(f"[INFO] Found GenshinImpact.exe window: {exe}")
        return h
    return None


def _activate_game():
    hwnd = _find_genshin_hwnd()
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


def _get_game_resolution():
    if FORCE_RESOLUTION:
        print(f"[INFO] Resolution forced to {FORCE_RESOLUTION[0]}x{FORCE_RESOLUTION[1]}")
        return FORCE_RESOLUTION

    hwnd = _find_genshin_hwnd()
    if hwnd:
        l, t, r, b = win32gui.GetWindowRect(hwnd)
        w, h = r - l, b - t
        print(f"[INFO] Genshin window rect: ({l},{t}) -> ({r},{b})  size={w}x{h}")
        if w > 800 and h > 600:
            return w, h
        print(f"[WARN] Window size looks wrong, falling back to largest monitor")
    else:
        print("[WARN] Genshin Impact window not found, falling back to largest monitor")

    with mss.mss() as sct:
        largest = max(sct.monitors[1:], key=lambda m: m["width"] * m["height"])
        print(f"[INFO] Largest monitor: {largest['width']}x{largest['height']}")
        return largest["width"], largest["height"]


SCREEN_W, SCREEN_H = _get_game_resolution()

_profile = _PROFILES.get((SCREEN_W, SCREEN_H))
if _profile is None:
    print(f"[WARN] No profile for {SCREEN_W}x{SCREEN_H}, scaling from {_REF_W}x{_REF_H}")
    _profile = _scale_profile(SCREEN_W, SCREEN_H)
else:
    print(f"[INFO] Profile loaded for {SCREEN_W}x{SCREEN_H}")

COLUMNS = _profile["columns"]
HIT_LINE_Y = _profile["hit_line_y"]
TOP_Y = _profile["top_y"]
DETECT_Y = _profile["detect_y"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QUIT_KEY = win32con.VK_F8  # key to stop the bot while the game has focus

pydirectinput.PAUSE = 0  # default is 0.05s per action - kills timing

YELLOW = np.array([253, 176, 85])
PURPLE = np.array([165, 138, 255])
TOLERANCE = 30
COOLDOWN = 0.12

COL_LEFT = int(min(COLUMNS.values())) - 10
HOLD_TIMEOUT = 5.0
CONFIRM_FRAMES = 6
WATCH_INTERVAL = 0.016
CAPTURE_INTERVAL = 0.016
HOLD_INTERVAL = 0.016

last_hit = {key: 0.0 for key in COLUMNS}
holding = {key: False for key in COLUMNS}
executor = ThreadPoolExecutor(max_workers=len(COLUMNS) * 4)
stop_event = threading.Event()

shared_frame = None
frame_lock = threading.Lock()


# -- Capture ------------------------------------------------------------------


def capture_loop():
    global shared_frame
    zone = {
        "left": COL_LEFT,
        "top": TOP_Y,
        "width": int(max(COLUMNS.values())) - COL_LEFT + 10,
        "height": HIT_LINE_Y - TOP_Y,
    }
    with mss.mss() as sct:
        while not stop_event.is_set():
            frame = np.array(sct.grab(zone))[:, :, :3][:, :, ::-1]
            with frame_lock:
                shared_frame = frame
            time.sleep(CAPTURE_INTERVAL)


# -- Detection ----------------------------------------------------------------


def _get_frame():
    with frame_lock:
        return shared_frame


def get_note(col_x, target_y):
    frame = _get_frame()
    if frame is None:
        return None
    ox = int(col_x) - COL_LEFT
    oy = target_y - TOP_Y
    x1, x2 = max(0, ox - 2), min(frame.shape[1], ox + 3)
    y1, y2 = max(0, oy - 2), min(frame.shape[0], oy + 3)
    patch = frame[y1:y2, x1:x2]
    if patch.size == 0:
        return None
    diff_y = np.abs(patch.astype(int) - YELLOW).mean(axis=2).min()
    diff_p = np.abs(patch.astype(int) - PURPLE).mean(axis=2).min()
    if diff_y < TOLERANCE and diff_y < diff_p:
        return "yellow"
    if diff_p < TOLERANCE:
        return "purple"
    return None


def note_still_present(col_x):
    frame = _get_frame()
    if frame is None:
        return False
    ox = int(col_x) - COL_LEFT
    oy = HIT_LINE_Y - TOP_Y
    x1, x2 = max(0, ox - 2), min(frame.shape[1], ox + 2)
    y1, y2 = max(0, oy - 60), min(frame.shape[0], oy + 10)
    patch = frame[y1:y2, x1:x2]
    return np.abs(patch.astype(int) - PURPLE).mean(axis=2).min() < 60


# -- Hit ----------------------------------------------------------------------


def wait_release(col_x):
    consecutive = 0
    deadline = time.time() + HOLD_TIMEOUT
    while consecutive < CONFIRM_FRAMES:
        if stop_event.is_set() or time.time() > deadline:
            break
        if note_still_present(col_x):
            consecutive = 0
        else:
            consecutive += 1
        time.sleep(HOLD_INTERVAL)


def hit_key(key, kind, col_x):
    try:
        if kind == "yellow":
            print(f"[YELLOW] {key}")
            pydirectinput.press(key.lower())
        elif kind == "purple":
            print(f"[PURPLE START] {key}")
            holding[key] = True
            pydirectinput.keyDown(key.lower())
            wait_release(col_x)
            pydirectinput.keyUp(key.lower())
            holding[key] = False
            print(f"[PURPLE END] {key}")
    except Exception as e:
        holding[key] = False
        print(f"[ERR] hit_key {key}: {e}")


# -- Column watcher -----------------------------------------------------------


def watch_column(key, col_x):
    while not stop_event.is_set():
        note = get_note(col_x, DETECT_Y)
        now = time.time()
        if note and not holding[key] and (now - last_hit[key]) > COOLDOWN:
            delta = now - last_hit[key]
            last_hit[key] = now
            print(f"[HIT] {key} {note}  delta={delta:.3f}")
            executor.submit(hit_key, key, note, col_x)
        time.sleep(WATCH_INTERVAL)


# -- Overlay ------------------------------------------------------------------

# Physical pixels (mss/win32) vs tkinter logical pixels differ when DPI scaling is active.
# _dpi converts a physical coordinate to the logical pixel space tkinter draws in.
_dpi_scale = ctypes.windll.user32.GetDpiForSystem() / 96.0
_WIN_W = int(SCREEN_W / _dpi_scale)
_WIN_H = int(SCREEN_H / _dpi_scale)
print(f"[INFO] DPI scale: {_dpi_scale:.3f}  overlay window: {_WIN_W}x{_WIN_H}")


def _px(v):
    return int(v / _dpi_scale)


def quit_app():
    stop_event.set()
    executor.shutdown(wait=False)
    try:
        root.destroy()
    except Exception:
        pass


root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-transparentcolor", "black")
root.attributes("-alpha", 0.8)
root.geometry(f"{_WIN_W}x{_WIN_H}+0+0")

canvas = tk.Canvas(root, width=_WIN_W, height=_WIN_H, bg="black", highlightthickness=0)
canvas.pack()

btn_quit = tk.Button(
    root,
    text="[X] Quit  (F8)",
    command=quit_app,
    bg="#ff4444",
    fg="white",
    font=("Arial", 11, "bold"),
    relief="flat",
    padx=8,
    pady=4,
)
btn_quit.place(x=20, y=20)
root.bind("<Escape>", lambda e: quit_app())


def _poll_quit_key():
    if not stop_event.is_set() and win32api.GetAsyncKeyState(QUIT_KEY) & 1:
        root.after(0, quit_app)
        return
    root.after(100, _poll_quit_key)

threading.Thread(target=capture_loop, daemon=True).start()
for key, col_x in COLUMNS.items():
    threading.Thread(target=watch_column, args=(key, col_x), daemon=True).start()

_activate_game()
_poll_quit_key()


def draw_overlay():
    if stop_event.is_set():
        return
    canvas.delete("all")
    for key, x in COLUMNS.items():
        canvas.create_line(_px(x), _px(TOP_Y), _px(x), _px(HIT_LINE_Y), fill="lime", width=2)
        canvas.create_text(
            _px(x), _px(TOP_Y) - 15, text=key, fill="lime", font=("Arial", 14, "bold")
        )
    canvas.create_line(0, _px(HIT_LINE_Y), _WIN_W, _px(HIT_LINE_Y), fill="red", width=2)
    canvas.create_line(0, _px(DETECT_Y), _WIN_W, _px(DETECT_Y), fill="cyan", width=1)
    root.after(16, draw_overlay)


signal.signal(signal.SIGINT, lambda *_: root.after(0, quit_app))

draw_overlay()
try:
    root.mainloop()
except KeyboardInterrupt:
    quit_app()
