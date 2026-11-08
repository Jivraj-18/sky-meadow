#!/usr/bin/env python3
"""Playtest video with the game's soundtrack: make_video_with_audio.py RUN_NAME OUT.mp4 [--small]

Rebuilds the audio from the editor log (music start/stop and every "Platformer: sound X" event,
mixed from assets_src/audio at the logged times) and muxes it with the run's frames.
--small: 854x480, high-efficiency settings for the smallest file that still looks good.
"""
import os
import re
import subprocess
import sys
import tempfile
import wave
from datetime import datetime

import numpy as np

HOME = os.path.expanduser("~/unreal-tests")
LOG = os.environ.get("PLAYTEST_LOG", HOME + "/RealWorldGame/Saved/Logs/RealWorldGame.log")
AUDIO = HOME + "/assets_src/audio/"
SR = 44100


def load(name):
    with wave.open(AUDIO + name + ".wav") as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768


def stamp(line):
    return datetime.strptime(re.match(r"\[(\S+?)\]", line).group(1), "%Y.%m.%d-%H.%M.%S:%f").timestamp()


def main():
    run, out = sys.argv[1], sys.argv[2]
    small = "--small" in sys.argv
    lines = open(LOG, errors="ignore").read().splitlines()
    start = max(i for i, l in enumerate(lines) if "PLAYTEST STARTED %s " % run in l)
    events = lines[start:]
    events = events[:next(i for i, l in enumerate(events) if "PLAYTEST DONE" in l) + 1]
    t0, t1 = stamp(events[0]), stamp(events[-1])

    mix = np.zeros(int((t1 - t0 + 4) * SR))
    music_on = next((stamp(l) - t0 for l in events if "Platformer: music" in l), None)
    if music_on is not None:
        off = next((stamp(l) - t0 for l in events if re.search(r"sound \S+::(LevelComplete|GameOver)", l)), t1 - t0)
        track = load("MUS_SkyMeadow") * 0.55
        i0, i1 = int(music_on * SR), int(off * SR)
        mix[i0:i1] += np.tile(track, (i1 - i0) // len(track) + 1)[:i1 - i0]
    for l in events:
        m = re.search(r"Platformer: sound EPlatformerSound::(\w+)", l)
        if m:
            s = load("SFX_" + m.group(1))
            i = int((stamp(l) - t0) * SR)
            mix[i:i + len(s)] += s[:len(mix) - i]
    mix /= max(1.0, np.abs(mix).max())

    run_dir = HOME + "/RealWorldGame/Saved/Playtest/" + run
    fps = len([f for f in os.listdir(run_dir) if f.startswith("f_")]) / (t1 - t0)
    with tempfile.TemporaryDirectory() as tmp:
        with wave.open(tmp + "/a.wav", "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((mix * 32767).astype(np.int16).tobytes())
        subprocess.run([sys.executable, HOME + "/tools/make_video.py", tmp + "/v.mp4", run_dir, "--fps", "%.3f" % fps],
                       check=True, stdout=subprocess.DEVNULL)
        video = ["-vf", "scale=854:480", "-c:v", "libx264", "-preset", "veryslow", "-crf", "28", "-tune", "animation",
                 "-pix_fmt", "yuv420p"] if small else ["-c:v", "copy"]
        audio = ["-c:a", "aac", "-b:a", "64k" if small else "160k"]
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp + "/v.mp4", "-i", tmp + "/a.wav", *video,
                        *audio, "-movflags", "+faststart", "-shortest", out], check=True)
    print("wrote %s (%.1f s, %.0f KB)" % (out, t1 - t0, os.path.getsize(out) / 1024))


if __name__ == "__main__":
    main()
