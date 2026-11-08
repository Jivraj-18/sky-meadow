"""Draw the HUD icons (heart full/empty, coin) as PNGs matching the kit's cartoon style.

Drawn at 4x and downsampled for smooth edges. Output: assets_src/ui/*.png (256 px).
"""
import math
import os

from PIL import Image, ImageDraw

OUT = os.path.expanduser("~/unreal-tests/assets_src/ui")
SIZE, SS = 256, 4
S = SIZE * SS
OUTLINE = (40, 24, 20, 255)
os.makedirs(OUT, exist_ok=True)


def heart_polygon(cx, cy, r, steps=200):
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * r / 17, cy - y * r / 17))
    return pts


def save(img, name):
    img.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(OUT, name))
    print("wrote", name)


def heart(filled):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S / 2
    d.polygon(heart_polygon(c, c + S * 0.03, S * 0.46), fill=OUTLINE)
    if filled:
        d.polygon(heart_polygon(c, c + S * 0.03, S * 0.40), fill=(232, 52, 64, 255))
        d.polygon(heart_polygon(c, c + S * 0.06, S * 0.30), fill=(255, 92, 100, 255))
        d.ellipse((S * 0.25, S * 0.26, S * 0.40, S * 0.40), fill=(255, 220, 220, 255))  # shine
    else:
        d.polygon(heart_polygon(c, c + S * 0.03, S * 0.40), fill=(120, 110, 110, 170))
    return img


def coin():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = S * 0.04
    d.ellipse((m, m, S - m, S - m), fill=OUTLINE)
    m += S * 0.05
    d.ellipse((m, m, S - m, S - m), fill=(214, 150, 30, 255))   # rim
    m += S * 0.07
    d.ellipse((m, m, S - m, S - m), fill=(255, 205, 60, 255))   # face
    c, ro, ri = S / 2, S * 0.26, S * 0.11
    star = [(c + (ro if i % 2 == 0 else ri) * math.sin(math.pi * i / 5),
             c - (ro if i % 2 == 0 else ri) * math.cos(math.pi * i / 5)) for i in range(10)]
    d.polygon(star, fill=(214, 150, 30, 255))
    d.ellipse((S * 0.24, S * 0.20, S * 0.36, S * 0.32), fill=(255, 245, 200, 255))  # shine
    return img


save(heart(True), "T_HeartFull.png")
save(heart(False), "T_HeartEmpty.png")
save(coin(), "T_Coin.png")
