"""Bot route through Lvl_Course01 (see build_course01.py for the layout)."""
import importlib
import os
import sys

import unreal

sys.path.insert(0, os.path.expanduser("~/unreal-tests/tools"))
import autoplay  # noqa: E402
importlib.reload(autoplay)
from autoplay import board_platform, go, launch_and_land, ride_platform, run_jump, wait_platform  # noqa: E402

ROUTE = [
    go(700),                                     # A: collect coins at 300-500
    run_jump(760, 1250, jumps=2),                # gap 900-1050, grab the mid-air coin
    go(1500, tol=60),                            # onto the jump pad -> launched
    launch_and_land(2250),                       # C: high brick ledge, coins 2100-2300
    go(2480),                                    # wait well back from the edge of C (ends 2655)
    wait_platform(unreal.MovingPlatform, 2860),  # platform back at its start
    board_platform(unreal.MovingPlatform, 2600),  # jump from the ledge edge
    ride_platform(unreal.MovingPlatform, 3540),
    run_jump(3600, 4200, jumps=2),               # hop to the finish ledge and the goal flag
]

autoplay.start("course01", ROUTE)
