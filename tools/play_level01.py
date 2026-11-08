"""Bot route through Lvl_World1_1 (see build_level01.py for the layout)."""
import importlib
import os
import sys

import unreal

sys.path.insert(0, os.path.expanduser("~/unreal-tests/tools"))
import autoplay  # noqa: E402
importlib.reload(autoplay)
from autoplay import (board_platform, go, hop_up, launch_and_land, reach_goal,  # noqa: E402
                      ride_platform, run_jump, stomp, wait_platform)

MP = unreal.MovingPlatform
ROUTE = [
    go(300),                           # 1 wait for the crab (patrols 700-1000)
    stomp(),                           #   crab, then on to the coins
    go(1100),
    run_jump(1200, 1600, jumps=3),     # 1.9 m gap to island 1 (meadow ends 1255, island 1445-1755)
    run_jump(1700, 2000, jumps=1),     # island 2 (+0.5 m, 1845-2155)
    run_jump(2100, 2400, jumps=1),     # island 3 (+0.5 m, 2245-2555)
    run_jump(2500, 2750, jumps=1),     # island 4 (+0.5 m, 2645-2955)
    go(2850),                          # 3 checkpoint 1 at 2800
    hop_up(3500),                      # 4 stairs to the plateau
    stomp(),                           # 5 monster patrolling 3700-3950
    go(4100, tol=60),                  # 5 jump pad -> launched
    launch_and_land(4530),             # 6 cloud ledge (starts 4445; land clear of the edge, before the skull)
    stomp(),                           #   skull patrolling 4550-4800
    go(4900),                          # wait back from the edge (ends 5055)
    wait_platform(MP, 5210),
    board_platform(MP, 4980),
    ride_platform(MP, 5890),           # 7 sky gap
    go(6300),                          # 8 checkpoint 2
    stomp(),                           #   crab patrolling 6500-6900 (bee overhead)
    reach_goal(7150),                  # goal flag
]

autoplay.start("level01", ROUTE)
