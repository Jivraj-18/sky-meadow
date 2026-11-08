"""Build /Game/Maps/Lvl_World1_1 "Sky Meadow" - the first real level.

Sections along +X (block z = centre, walkable top = z + 50):
  1 Meadow        x    0-1200  top   50  wide start, coins, ? blocks
  2 Islands       x 1500-2900  top 50-200 four 3 m islands, each 0.5 m higher
  3 Checkpoint 1  x 2800
  4 Stairs        x 3000-3500  top 200-450 brick steps
  5 Plateau       x 3600-4200  top  450  bridge plateau, jump pad at 4100
  6 Cloud ledge   x 4500-5000  top  800
  7 Sky gap       x 5200-5900  moving platform, top level with the ledges
  8 Finish        x 6100-7300  top  800  checkpoint 2, goal flag at 7150, tower behind
"""
import importlib
import os
import random
import sys

sys.path.insert(0, os.path.expanduser("~/unreal-tests/tools"))
import levelkit as lk  # noqa: E402
importlib.reload(lk)
import unreal  # noqa: E402

LEVEL = "/Game/Maps/Lvl_World1_1"
NATURE = "/Game/Kit/Nature/"
random.seed(11)

lk.new_level(LEVEL)
lk.sky_and_light()
lk.use_platforming_game_mode()
lk.spawn(unreal.PlayerStart, 0, 0, 150, label="PlayerStart")

# 1 Meadow ----------------------------------------------------------------------------------
lk.strip("BP_GrassBlock", -200, 1200, 0, lanes=lk.LANES5)
lk.coins([(x, 0, 50) for x in range(400, 801, 100)])
for x in (550, 650):
    lk.block("BP_QuestionBlock", x, 0, 330)
lk.block("BP_BrickBlock", 600, 0, 330)
for x, y in ((-100, 200), (300, -200), (900, 200), (1150, -200)):
    lk.prop(NATURE + "Bush", x, y, 50, 0.3, yaw=random.uniform(0, 360))
lk.prop(NATURE + "Tree", -150, -200, 50, 0.35)
lk.prop(NATURE + "Tree_Fruit", 1100, 200, 50, 0.3)

# 2 Islands: 3x3 islands, each 50 cm higher, ~0.9 m gaps --------------------------------------
islands = [(1500, 0), (1900, 50), (2300, 100), (2700, 150)]   # (first block x, block z)
for x, z in islands:
    lk.strip("BP_GrassBlock", x, x + 200, z)
for (xa, za), (xb, zb) in zip([(1000, 0)] + islands, islands):
    lk.coins([((xa + 255 + xb - 55) // 2, 0, max(za, zb) + 150)])  # over each gap

# 3 Checkpoint 1 (on island 4, top 200) --------------------------------------------------------
lk.block("BP_Checkpoint", 2800, 0, 200, label="Checkpoint1")  # on the path so its trigger spans all lanes

# 4 Stairs: six brick steps rising 50 cm each -------------------------------------------------
for i, x in enumerate(range(3000, 3501, 100)):
    z = 150 + 50 * i
    for y in lk.LANES3:
        lk.block("BP_BrickBlock", x, y, z)
        lk.block("BP_DirtBlock", x, y, z - 100)       # fill under each step
    if i % 2 == 1:
        lk.coins([(x, 0, z + 50)])

# 5 Plateau with a bridge look and the jump pad ----------------------------------------------
lk.strip("BP_GrassBlock", 3600, 4200, 400)
lk.coins([(x, y, 450) for x in (3750, 3850) for y in (-100, 100)])
lk.block("BP_JumpPad", 4100, 0, 450, label="JumpPad")
lk.prop(NATURE + "Bush_Fruit", 3700, 120, 450, 0.3)

# 6 Cloud ledge ------------------------------------------------------------------------------
lk.strip("BP_GrassBlock", 4500, 5000, 750)
lk.coins([(x, 0, 800) for x in (4650, 4750, 4850)])

# 7 Sky gap: moving platform (1.4x cube, 2.8 m tall; centre 660 -> top 800) --------------------
lk.block("BP_MovingPlatform", 5200, 0, 660, label="MovingPlatform", kit_scale=1.4,
         end_offset=unreal.Vector(700, 0, 0), travel_time=2.5, pause_time=1.5)
lk.coins([(5500, 0, 1000)])

# 8 Finish: checkpoint 2, goal flag, tower --------------------------------------------------
lk.strip("BP_GrassBlock", 6100, 7300, 750, lanes=lk.LANES5)
lk.block("BP_Checkpoint", 6250, 0, 800, label="Checkpoint2")
lk.coins([(x, 0, 800) for x in range(6500, 6901, 100)])
lk.block("BP_GoalFlag", 7150, 0, 800, yaw=90.0, label="GoalFlag")
lk.prop("/Game/Kit/Level/Tower1", 7450, 0, 800, 0.6, yaw=180.0, label="Tower")
lk.prop("/Game/Kit/Level/Tower_Door", 7450, 0, 800, 0.6, yaw=180.0, label="TowerDoor")
for x, y in ((6400, -200), (7000, 200), (7250, -200)):
    lk.prop(NATURE + "Bush", x, y, 800, 0.3, yaw=random.uniform(0, 360))

# Enemies (placed with their origin on the block top) ---------------------------------------------
V = unreal.Vector
lk.block("BP_Crab", 700, 0, 50, label="Crab_Meadow", patrol_offset=V(300, 0, 0))  # well clear of the meadow edge (1255)
lk.block("BP_Monster", 3700, 0, 450, label="Monster_Plateau", patrol_offset=V(250, 0, 0))
lk.block("BP_Skull", 4720, 0, 800, label="Skull_Ledge", patrol_offset=V(180, 0, 0))
lk.block("BP_Crab", 6500, 0, 800, label="Crab_Finish", patrol_offset=V(400, 0, 0))
lk.block("BP_Bee", 6950, 0, 1300, label="Bee_Finish", patrol_offset=V(150, 0, 0))  # high, past the crab: only careless jumps hit it

# Safety net --------------------------------------------------------------------------------
lk.block("BP_KillZone", 3600, 0, -400, label="KillZone")

# Scenery: floating rock islands and clouds -----------------------------------------------------
for i in range(14):
    x = random.uniform(-500, 8000)
    y = random.choice((-1, 1)) * random.uniform(900, 2500)
    lk.prop(NATURE + random.choice(["RockPlatforms_1", "RockPlatforms_2", "RockPlatforms_Large"]),
            x, y, random.uniform(-600, 600), random.uniform(0.5, 1.0), yaw=random.uniform(0, 360),
            label="SkyIsland_%d" % i)
for i in range(18):
    lk.prop(NATURE + "Cloud_%d" % random.randint(1, 3), random.uniform(-1000, 8500),
            random.choice((-1, 1)) * random.uniform(600, 3000), random.uniform(-300, 1800),
            random.uniform(1.0, 2.5), yaw=random.uniform(0, 360), label="Cloud_%d" % i)

print("LEVEL BUILT", lk.save(), "actors")
