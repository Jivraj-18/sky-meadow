#!/usr/bin/env python3
"""Turn playtest frame folders into one MP4: make_video.py out.mp4 RUN_DIR [RUN_DIR...] [--fps N]

Frames taken with "shot showui" contain the whole editor window; the game viewport is found
(editor chrome is dark, the game view bright) and cropped out.
"""
import os
import statistics
import subprocess
import sys
import tempfile

from PIL import Image


def viewport_box(path):
    im = Image.open(path).convert("L")
    w, h = im.size
    px = im.load()
    mid = h // 2
    xs = [x for x in range(w) if statistics.mean(px[x, y] for y in range(mid - 100, mid + 100, 3)) > 70]
    x0, x1 = min(xs), max(xs)
    ys = [y for y in range(h) if statistics.mean(px[x, y] for x in range(x0 + 20, x1 - 20, 3)) > 70]
    return x0, min(ys), x1 + 1, max(ys) + 1


def main():
    args = sys.argv[1:]
    fps = 8
    if "--fps" in args:
        i = args.index("--fps")
        fps = float(args[i + 1])
        del args[i:i + 2]
    out, runs = args[0], args[1:]
    with tempfile.TemporaryDirectory() as tmp:
        n = 0
        for run in runs:
            frames = sorted(f for f in os.listdir(run) if f.startswith("f_") and f.endswith(".png"))
            if not frames:
                continue
            first = Image.open(os.path.join(run, frames[0]))
            box = viewport_box(os.path.join(run, frames[len(frames) // 2])) if first.size[1] > 700 else None
            for f in frames:
                im = Image.open(os.path.join(run, f)).convert("RGB")
                if box:
                    im = im.crop(box)
                im.resize((960, 540), Image.LANCZOS).save(os.path.join(tmp, "v_%05d.png" % n))
                n += 1
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps),
                        "-i", os.path.join(tmp, "v_%05d.png"), "-c:v", "libx264", "-crf", "21",
                        "-pix_fmt", "yuv420p", out], check=True)
    print("wrote %s (%d frames)" % (out, n))


if __name__ == "__main__":
    main()
