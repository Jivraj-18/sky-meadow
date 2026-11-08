"""Heightmap for the quarry-edge scene (reference: grassy plateau dropping into a rocky quarry).

Writes assets_src/terrain/quarry_505.r16 (505x505, 16-bit little-endian) for a landscape with
1 m between vertices, plus a shaded preview PNG. Unreal convention: value 32768 = 0 m and, at
landscape Z scale 100, one unit = 100/128 cm.
"""
import os

import numpy as np
from PIL import Image

N = 505                      # vertices per side -> 504 m at 1 m spacing
OUT = os.path.expanduser("~/unreal-tests/assets_src/terrain")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

coords = np.linspace(-252, 252, N)
X, Y = np.meshgrid(coords, coords)  # metres; X east, Y south (Unreal +Y)


def value_noise(scale_m, octaves=5, persistence=0.5):
    """Smooth fractal noise in [-1, 1] by summing bilinear-interpolated random grids."""
    total = np.zeros((N, N))
    amp, freq, norm = 1.0, 1.0 / scale_m, 0.0
    for _ in range(octaves):
        cells = int(504 * freq) + 3
        grid = rng.uniform(-1, 1, (cells, cells))
        gx = (X + 252) * freq
        gy = (Y + 252) * freq
        x0, y0 = np.floor(gx).astype(int), np.floor(gy).astype(int)
        tx, ty = gx - x0, gy - y0
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)  # smoothstep
        a, b = grid[y0, x0], grid[y0, x0 + 1]
        c, d = grid[y0 + 1, x0], grid[y0 + 1, x0 + 1]
        total += amp * ((a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty)
        norm += amp
        amp *= persistence
        freq *= 2.0
    return total / norm


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# Plateau: gentle rolling grassland, rising into hills toward the map edges (skyline).
h = 4.0 * value_noise(90) + 1.5 * value_noise(25)
r_edge = np.sqrt(X ** 2 + Y ** 2)
h += 18.0 * smoothstep(150, 250, r_edge) * (0.6 + 0.4 * value_noise(60))

# Quarry: irregular pit east of centre, ~22 m deep, steep walls with two benches.
qx, qy = 55.0, 10.0
d = np.sqrt(((X - qx) / 75.0) ** 2 + ((Y - qy) / 55.0) ** 2)   # 1.0 = rim
d += 0.12 * value_noise(30, octaves=4)                            # ragged rim
depth = 22.0
inside = 1.0 - smoothstep(0.80, 1.0, d)                           # 1 in the pit, 0 outside
benches = (np.floor(inside * 3.0) / 3.0) * 0.55 + inside * 0.45  # stepped walls
h -= depth * benches
h += 1.2 * value_noise(12, octaves=3) * inside                    # rubbly floor

# A few rocky knolls on the plateau for boulders to sit on.
for kx, ky, kr, kh in [(-60, -40, 18, 3.0), (-20, 70, 14, 2.5), (110, -80, 16, 3.5)]:
    h += kh * np.exp(-((X - kx) ** 2 + (Y - ky) ** 2) / (2 * kr ** 2))

units = np.clip(32768 + h * 100 * 1.28, 0, 65535).astype("<u2")
units.tofile(os.path.join(OUT, "quarry_505.r16"))

# Shaded relief preview (light from the north-west) with height tint.
gy, gx = np.gradient(h)
shade = np.clip(0.6 + (-gx * 0.7 - gy * 0.7) * 0.35, 0, 1)
tint = (h - h.min()) / (h.max() - h.min())
rgb = np.stack([shade * (0.45 + 0.4 * tint), shade * (0.55 + 0.3 * tint), shade * (0.35 + 0.2 * tint)], -1)
Image.fromarray((rgb * 255).astype(np.uint8)).save(os.path.join(OUT, "quarry_preview.png"))
print("height range %.1f .. %.1f m, quarry floor ~%.1f m" % (h.min(), h.max(), h[int((qy + 252)), int(qx + 252)]))
