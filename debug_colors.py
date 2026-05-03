"""
Run this while the game is open with notes visible.
Press Enter to sample colors at detect_y for all columns.
Press Q+Enter to quit.
"""
import time
import numpy as np
import mss
from config import Config

cfg = Config()

zone = {
    "left": cfg.zone_left,
    "top": cfg.zone_top,
    "width": cfg.zone_width,
    "height": cfg.zone_height,
}

print(f"Sampling at y={cfg.detect_y} (detect line)")
print(f"Yellow target: {cfg.yellow}  tolerance={cfg.tolerance}")
print(f"Purple target: {cfg.purple}  tolerance={cfg.tolerance}")
print(f"Zone: left={cfg.zone_left} top={cfg.zone_top} w={cfg.zone_width} h={cfg.zone_height}")
print()
print("Press Enter to sample, Q+Enter to quit.")

with mss.mss() as sct:
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "q":
            break

        raw = np.array(sct.grab(zone))[:, :, :3][:, :, ::-1]
        oy = cfg.detect_y - cfg.top_y

        print(f"{'KEY':>4}  {'col_x':>6}  {'RGB at detect_y':>20}  {'diff_yellow':>12}  {'diff_purple':>12}  {'result':>8}")
        for key, col_x in cfg.columns.items():
            ox = int(col_x) - cfg.zone_left
            x1, x2 = max(0, ox - 2), min(raw.shape[1], ox + 2)
            y1, y2 = max(0, oy - 20), min(raw.shape[0], oy + 20)
            patch = raw[y1:y2, x1:x2]

            if patch.size == 0:
                print(f"{key:>4}  {col_x:>6.1f}  {'OUT OF BOUNDS':>20}")
                continue

            mean_color = patch.mean(axis=(0, 1)).astype(int)
            diff_y = np.abs(patch.astype(int) - cfg.yellow).mean(axis=2).min()
            diff_p = np.abs(patch.astype(int) - cfg.purple).mean(axis=2).min()

            if diff_y < cfg.tolerance and diff_y < diff_p:
                result = "YELLOW"
            elif diff_p < cfg.tolerance:
                result = "PURPLE"
            else:
                result = "-"

            print(f"{key:>4}  {col_x:>6.1f}  {str(list(mean_color)):>20}  {diff_y:>12.1f}  {diff_p:>12.1f}  {result:>8}")
        print()
