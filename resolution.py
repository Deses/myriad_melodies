import mss
import win32api
import win32gui
import win32process

_REF_W, _REF_H = 1920, 1080
_REF_COLUMNS = {"Q": 418.5, "S": 634.5, "D": 851.5, "J": 1067.5, "K": 1284.5, "L": 1500.5}
_REF_HIT_LINE_Y = 920
_REF_TOP_Y = 60
_REF_DETECT_Y = 850

# Add entries here when you calibrate a new resolution manually.
# Proportional scaling is used as fallback for unknown resolutions.
PROFILES = {
    (1920, 1080): {
        "columns": _REF_COLUMNS,
        "hit_line_y": _REF_HIT_LINE_Y,
        "top_y": _REF_TOP_Y,
        "detect_y": _REF_DETECT_Y,
    },
    (3440, 1440): {
        "columns": {"Q": 998.0, "S": 1287.0, "D": 1575.0, "J": 1864.0, "K": 2153.0, "L": 2441.0},
        "hit_line_y": 1227,
        "top_y": 100,
        "detect_y": 1130,
    },
    (1920, 1200): {
        "columns": {"Q": 418.5, "S": 634.5, "D": 851.5, "J": 1067.5, "K": 1284.5, "L": 1500.5},
        "hit_line_y": 1022,
        "top_y": 67,
        "detect_y": 944,
    },
    (2560, 1440): {
        "columns": {"Q": 406.0, "S": 614.0, "D": 826.0, "J": 1037.0, "K": 1248.0, "L": 1458.0},
        "hit_line_y": 894,
        "top_y": 60,
        "detect_y": 822,
    },
    (2560, 1080): {
        "columns": {"Q": 580.0, "S": 747.0, "D": 915.0, "J": 1084.0, "K": 1253.0, "L": 1425.0},
        "hit_line_y": 720,
        "top_y": 47,
        "detect_y": 665,
    },
}

# Override automatic detection. Set to e.g. (3440, 1440) if the wrong profile is loaded.
FORCE_RESOLUTION = None


def find_genshin_hwnd():
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
        print(f"[INFO] Found GenshinImpact.exe: {exe}")
        return h
    return None


def _scale_profile(sw, sh):
    sx, sy = sw / _REF_W, sh / _REF_H
    return {
        "columns": {k: round(v * sx, 1) for k, v in _REF_COLUMNS.items()},
        "hit_line_y": int(_REF_HIT_LINE_Y * sy),
        "top_y": int(_REF_TOP_Y * sy),
        "detect_y": int(_REF_DETECT_Y * sy),
    }


def get_profile():
    if FORCE_RESOLUTION:
        w, h = FORCE_RESOLUTION
        print(f"[INFO] Resolution forced to {w}x{h}")
    else:
        hwnd = find_genshin_hwnd()
        if hwnd:
            l, t, r, b = win32gui.GetWindowRect(hwnd)
            w, h = r - l, b - t
            print(f"[INFO] Genshin window: ({l},{t})->({r},{b})  size={w}x{h}")
            if not (w > 800 and h > 600):
                print("[WARN] Window size looks wrong, falling back to largest monitor")
                hwnd = None
        if not hwnd:
            print("[WARN] Genshin Impact window not found, falling back to largest monitor")
            with mss.mss() as sct:
                m = max(sct.monitors[1:], key=lambda m: m["width"] * m["height"])
                w, h = m["width"], m["height"]
            print(f"[INFO] Largest monitor: {w}x{h}")

    profile = PROFILES.get((w, h))
    if profile is None:
        print(f"[WARN] No profile for {w}x{h}, scaling from {_REF_W}x{_REF_H}")
        profile = _scale_profile(w, h)
    else:
        print(f"[INFO] Profile loaded for {w}x{h}")
    return w, h, profile
