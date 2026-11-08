"""Checks that falling after Checkpoint1 respawns the player there, not at the start."""
import importlib
import os
import sys

sys.path.insert(0, os.path.expanduser("~/unreal-tests/tools"))
import autoplay  # noqa: E402
importlib.reload(autoplay)
from autoplay import expect_near, fall_off_side, go, run_jump  # noqa: E402

ROUTE = [
    go(1100),
    run_jump(1200, 1600, jumps=3),
    run_jump(1700, 2000, jumps=2),
    run_jump(2100, 2400, jumps=2),
    run_jump(2500, 2750, jumps=2),
    go(2850),              # checkpoint 1 at 2800
    fall_off_side(),
    expect_near(2800),     # respawned at the checkpoint, not at x=0
]

autoplay.start("level01_checkpoint", ROUTE, stop_on_fall=False)
