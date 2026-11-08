"""Synthesize the game's sound effects and music (original chiptune) as 16-bit WAVs.

Output: assets_src/audio/*.wav. Everything is generated here, so it's free to use and edit:
change the notes or envelopes below and re-run.
"""
import os
import wave

import numpy as np

SR = 44100
OUT = os.path.expanduser("~/unreal-tests/assets_src/audio")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

NOTE_INDEX = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def hz(note):
    """'A4' -> 440 Hz."""
    name, octave = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((NOTE_INDEX[name] + 12 * (octave - 4) - 9) / 12)


def t_axis(seconds):
    return np.arange(int(SR * seconds)) / SR


def phase(freq, seconds):
    """Phase (cycles) for a constant or per-sample frequency."""
    f = np.broadcast_to(np.asarray(freq, dtype=float), t_axis(seconds).shape)
    return np.cumsum(f) / SR


def square(freq, seconds, duty=0.5):
    return np.where((phase(freq, seconds) % 1.0) < duty, 1.0, -1.0)


def triangle(freq, seconds):
    p = phase(freq, seconds) % 1.0
    return 4 * np.abs(p - 0.5) - 1


def sine(freq, seconds):
    return np.sin(2 * np.pi * phase(freq, seconds))


def noise(seconds):
    return rng.uniform(-1, 1, int(SR * seconds))


def env(seconds, attack=0.005, decay=0.1, sustain=0.6, release=0.05):
    n = int(SR * seconds)
    e = np.full(n, sustain)
    a, d, r = int(SR * attack), int(SR * decay), int(SR * release)
    e[:a] = np.linspace(0, 1, a, endpoint=False)
    e[a:a + d] = np.linspace(1, sustain, len(e[a:a + d]))
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def sweep(f0, f1, seconds, curve=1.0):
    x = np.linspace(0, 1, int(SR * seconds)) ** curve
    return f0 * (f1 / f0) ** x


def place(track, sound, at):
    i = int(at * SR)
    track[i:i + len(sound)] += sound[:max(0, len(track) - i)]


def save(name, data, peak_db=-3.0):
    data = data / (np.max(np.abs(data)) + 1e-9) * 10 ** (peak_db / 20)
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote %-18s %.2fs" % (name, len(data) / SR))


def tone(note, seconds, wave_fn=square, vol=1.0, **env_kw):
    f = hz(note) if isinstance(note, str) else note
    s = wave_fn(f, seconds) if wave_fn is not square else square(f, seconds, env_kw.pop("duty", 0.5))
    return s * env(seconds, **env_kw) * vol


# --- Sound effects ---------------------------------------------------------------------------

def sfx_jump():
    d = 0.18
    return square(sweep(320, 760, d, 0.7), d, 0.25) * env(d, decay=0.12, sustain=0.3, release=0.04)


def sfx_coin():
    a = tone("B5", 0.07, duty=0.25, decay=0.02, sustain=0.8, release=0.005)
    b = tone("E6", 0.38, duty=0.25, decay=0.3, sustain=0.0, release=0.05)
    return np.concatenate([a, b])


def sfx_stomp():
    d = 0.2
    thump = sine(sweep(220, 55, d, 0.5), d) * env(d, decay=0.15, sustain=0.0, release=0.02)
    crunch = noise(0.06) * env(0.06, attack=0.001, decay=0.05, sustain=0.0, release=0.005) * 0.5
    out = thump.copy()
    out[:len(crunch)] += crunch
    return out


def sfx_hurt():
    d = 0.45
    f = sweep(700, 180, d, 0.8) * (1 + 0.05 * np.sin(2 * np.pi * 18 * t_axis(d)))
    return square(f, d, 0.5) * env(d, decay=0.3, sustain=0.2, release=0.1)


def sfx_jump_pad():
    d = 0.4
    f = sweep(180, 980, d, 0.6) * (1 + 0.08 * np.sin(2 * np.pi * 14 * t_axis(d)))
    return sine(f, d) * 0.7 * env(d, decay=0.3, sustain=0.4, release=0.08) + \
        square(f / 2, d, 0.5) * 0.25 * env(d, decay=0.2, sustain=0.0, release=0.05)


def sfx_checkpoint():
    out = np.zeros(int(SR * 0.62))
    for i, n in enumerate(["C5", "E5", "G5", "C6"]):
        place(out, tone(n, 0.3 if i == 3 else 0.12, duty=0.25, decay=0.08, sustain=0.5, release=0.04), i * 0.075)
        place(out, tone(n, 0.3 if i == 3 else 0.12, triangle, 0.6, decay=0.08, sustain=0.5, release=0.04), i * 0.075)
    return out


def jingle(melody, bass, bpm, tail=0.6):
    beat = 60.0 / bpm
    length = sum(d for _, d in melody) * beat + tail
    out = np.zeros(int(SR * length))
    t = 0.0
    for n, d in melody:
        if n:
            place(out, tone(n, d * beat * 0.95, duty=0.25, decay=0.1, sustain=0.6, release=0.05), t)
            place(out, tone(n, d * beat * 0.95, triangle, 0.4, decay=0.1, sustain=0.6, release=0.05), t)
        t += d * beat
    t = 0.0
    for n, d in bass:
        if n:
            place(out, tone(n, d * beat * 0.9, triangle, 0.9, decay=0.05, sustain=0.8, release=0.05), t)
        t += d * beat
    return out


def sfx_level_complete():
    melody = [("G4", 0.5), ("C5", 0.5), ("E5", 0.5), ("G5", 1.0), ("E5", 0.5), ("G5", 2.5),
              (None, 0.25), ("A5", 0.25), ("B5", 0.25), ("C6", 2.0)]
    bass = [("C3", 1.5), ("C3", 1.5), ("E3", 1.0), ("F3", 1.0), ("G3", 1.25), ("C3", 2.0)]
    return jingle(melody, bass, 150, tail=0.8)


def sfx_game_over():
    melody = [("G4", 0.75), ("F#4", 0.75), ("F4", 0.75), ("E4", 2.5)]
    bass = [("C3", 2.25), ("C2", 2.5)]
    return jingle(melody, bass, 110, tail=0.6)


# --- Music: 8 bars at 132 BPM in C major, C - Am - F - G twice, seamless loop -----------------

def music_loop():
    bpm = 132
    beat = 60.0 / bpm
    bars = 8
    length = bars * 4 * beat
    out = np.zeros(int(SR * length))

    chords = [("C3", ["C4", "E4", "G4"]), ("A2", ["A3", "C4", "E4"]),
              ("F2", ["F3", "A3", "C4"]), ("G2", ["G3", "B3", "D4"])] * 2
    for bar, (root, triad) in enumerate(chords):
        t0 = bar * 4 * beat
        # Bass: root / fifth bounce on eighths (triangle).
        root_hz = hz(root)
        for i in range(8):
            f = root_hz * (1.5 if i % 4 == 2 else 1.0)
            place(out, tone(f, beat * 0.45, triangle, 0.55, decay=0.05, sustain=0.7, release=0.03), t0 + i * beat / 2)
        # Arpeggio: quiet 12.5% square sixteenths.
        for i in range(16):
            n = triad[i % 3] if i % 4 != 3 else triad[1]
            place(out, tone(n, beat * 0.22, duty=0.125, vol=0.12, decay=0.04, sustain=0.3, release=0.02),
                  t0 + i * beat / 4)

    # Melody (25% square), (note, beats) per bar; each bar sums to 4 beats.
    melody = [
        [("E5", 1), ("G5", 0.5), ("E5", 0.5), ("C5", 1), ("D5", 1)],
        [("E5", 1.5), ("C5", 0.5), ("A4", 2)],
        [("F5", 1), ("A5", 0.5), ("F5", 0.5), ("C5", 1), ("F5", 1)],
        [("G5", 1.5), ("F5", 0.5), ("D5", 1), ("B4", 1)],
        [("C5", 0.5), ("E5", 0.5), ("G5", 0.5), ("C6", 0.5), ("B5", 1), ("G5", 1)],
        [("A5", 1), ("E5", 1), ("C5", 1), ("E5", 1)],
        [("F5", 0.5), ("E5", 0.5), ("D5", 0.5), ("C5", 0.5), ("A4", 1), ("C5", 1)],
        [("D5", 1), ("G4", 0.5), ("B4", 0.5), ("D5", 1), (None, 1)],
    ]
    for bar, notes in enumerate(melody):
        t = bar * 4 * beat
        for n, d in notes:
            if n:
                place(out, tone(n, d * beat * 0.9, duty=0.25, vol=0.32, decay=0.08, sustain=0.55, release=0.04), t)
            t += d * beat

    # Drums: kick on 1 and 3, snare on 2 and 4, closed hats on eighths.
    kick = sine(sweep(150, 45, 0.15, 0.4), 0.15) * env(0.15, attack=0.001, decay=0.12, sustain=0.0, release=0.02)
    snare = noise(0.12) * env(0.12, attack=0.001, decay=0.1, sustain=0.0, release=0.01) * 0.35
    hat = noise(0.03) * env(0.03, attack=0.001, decay=0.025, sustain=0.0, release=0.004) * 0.12
    for b in range(bars * 4):
        t = b * beat
        place(out, kick * 0.8 if b % 2 == 0 else snare, t)
        place(out, hat, t)
        place(out, hat, t + beat / 2)

    return out[:int(SR * length)]


save("SFX_Jump", sfx_jump())
save("SFX_Coin", sfx_coin())
save("SFX_Stomp", sfx_stomp())
save("SFX_Hurt", sfx_hurt())
save("SFX_JumpPad", sfx_jump_pad())
save("SFX_Checkpoint", sfx_checkpoint())
save("SFX_LevelComplete", sfx_level_complete())
save("SFX_GameOver", sfx_game_over())
save("MUS_SkyMeadow", music_loop(), peak_db=-6.0)
