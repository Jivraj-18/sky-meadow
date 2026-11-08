"""Checks lives: each fall costs one, and losing the last one is game over (then a restart)."""
import importlib
import os
import sys

sys.path.insert(0, os.path.expanduser("~/unreal-tests/tools"))
import autoplay  # noqa: E402
importlib.reload(autoplay)
from autoplay import expect_game_over, expect_hud, expect_lives, fall_off_side, wait  # noqa: E402

ROUTE = [
    expect_lives(3), expect_hud("hearts=3"),
    fall_off_side(), wait(2.0), expect_lives(2), expect_hud("hearts=2"),   # wait out the 1.5 s invulnerability
    fall_off_side(), wait(2.0), expect_lives(1),
    fall_off_side(), expect_lives(0), expect_game_over(), expect_hud("banner='GAME OVER"),
    wait(4.0), expect_lives(3), expect_hud("hearts=3"),  # level restarted 2.5 s later, HUD reset
]

autoplay.start("level01_gameover", ROUTE, stop_on_fall=False)
