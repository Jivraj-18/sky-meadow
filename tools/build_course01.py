"""Build /Game/Maps/Lvl_Course01: a short test course exercising every building block.

The course runs along +X. Blocks are 1 m cubes (top surface 50 cm above their centre).
Re-running rebuilds the level from scratch.
"""
import unreal

LEVEL = "/Game/Maps/Lvl_Course01"
lib = unreal.EditorAssetLibrary
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# Works headless or in a live editor; a level can't be deleted while it is open.
if lib.does_asset_exist(LEVEL):
    levels.load_level("/Game/ThirdPerson/Lvl_ThirdPerson")
    lib.delete_asset(LEVEL)
levels.new_level(LEVEL)


def bp(name):
    return unreal.load_asset("/Game/Blocks/" + name).generated_class()


def spawn(cls, x, y=0.0, z=0.0, yaw=0.0, label=None, **props):
    a = actors.spawn_actor_from_class(cls, unreal.Vector(x, y, z), unreal.Rotator(0.0, 0.0, yaw))
    for k, v in props.items():
        a.set_editor_property(k, v)  # editor property change re-runs construction
    if label:
        a.set_actor_label(label)
    return a


def row(block, x0, x1, z, step=100, lanes=(-100, 0, 100)):
    """A strip of blocks along X, three blocks (3.3 m) wide."""
    for x in range(x0, x1 + 1, step):
        for y in lanes:
            spawn(bp(block), x, y, z)


# --- Sky and light -----------------------------------------------------------------------
spawn(unreal.DirectionalLight, 0, 0, 2000, label="Sun").set_actor_rotation(
    unreal.Rotator(-15.0, -50.0, 35.0), False)  # roll, pitch, yaw
sky = spawn(unreal.SkyLight, 0, 0, 1000, label="SkyLight")
sky.light_component.set_editor_property("real_time_capture", True)
spawn(unreal.SkyAtmosphere, 0, 0, 0, label="SkyAtmosphere")
spawn(unreal.ExponentialHeightFog, 0, 0, -600, label="Fog")

# --- Course ------------------------------------------------------------------------------
spawn(unreal.PlayerStart, 0, 0, 150, label="PlayerStart")

# A: start runway with coins and a question block overhead
row("BP_GrassBlock", 0, 800, 0)
for x in (300, 400, 500):
    spawn(bp("BP_Coin"), x, 0, 110, label="Coin_A_%d" % x)
spawn(bp("BP_QuestionBlock"), 650, 0, 330, label="QuestionBlock")

# Gap (2 m) with a coin to grab mid-jump
spawn(bp("BP_Coin"), 950, 0, 220, label="Coin_Gap")

# B: runway ending in a jump pad
row("BP_GrassBlock", 1100, 1600, 0)
spawn(bp("BP_JumpPad"), 1500, 0, 50, label="JumpPad")

# C: high brick ledge with coins
row("BP_BrickBlock", 1900, 2600, 450)
for x in (2100, 2200, 2300):
    spawn(bp("BP_Coin"), x, 0, 560, label="Coin_C_%d" % x)

# D: moving platform across a 9 m gap
# 1.4x cube is 2.8 m tall; centre at 360 puts its top (500) level with both ledges.
spawn(bp("BP_MovingPlatform"), 2850, 0, 360, label="MovingPlatform", kit_scale=1.4,
      end_offset=unreal.Vector(700, 0, 0), travel_time=2.5, pause_time=1.5)

# E: finish ledge and goal
row("BP_GrassBlock", 3800, 4300, 450)
spawn(bp("BP_GoalFlag"), 4200, 0, 500, label="GoalFlag")

# Safety net below everything
spawn(bp("BP_KillZone"), 2000, 0, -400, label="KillZone")

# --- Decoration ----------------------------------------------------------------------------
def prop(mesh_path, x, y, z, scale, label):
    # spawn_actor_from_object needs the editor placement UI, which a headless run lacks.
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z))
    a.static_mesh_component.set_static_mesh(unreal.load_asset(mesh_path))
    a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    a.set_actor_label(label)


for i, (x, y, z) in enumerate([(500, -900, 900), (1800, 1100, 1200), (3200, -1000, 1000), (4400, 900, 1300)]):
    prop("/Game/Kit/Nature/Cloud_%d" % (i % 3 + 1), x, y, z, 1.5, "Cloud_%d" % i)
for x in (100, 1200, 4300):
    prop("/Game/Kit/Nature/Bush", x, 40, 50 if x < 3000 else 500, 0.3, "Bush_%d" % x)

# Platforming character via the level's game mode
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property(
    "default_game_mode",
    unreal.load_asset("/Game/Variant_Platforming/Blueprints/BP_PlatformingGameMode").generated_class())

levels.save_current_level()
print("COURSE BUILT", len(actors.get_all_level_actors()), "actors")
