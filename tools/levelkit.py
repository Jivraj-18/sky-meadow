"""Helpers for building levels from the /Game/Blocks building blocks.

Coordinates: the course runs along +X; blocks are 1 m cubes whose top is 50 cm above the
z you place them at. Works headless or inside a live editor.
"""
import unreal

lib = unreal.EditorAssetLibrary
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

LANES3 = (-100, 0, 100)
LANES5 = (-200, -100, 0, 100, 200)


def new_level(path):
    """Create an empty level at path, replacing any existing one."""
    if lib.does_asset_exist(path):
        # A level can't be deleted while it is open.
        levels.load_level("/Game/ThirdPerson/Lvl_ThirdPerson")
        lib.delete_asset(path)
    levels.new_level(path)


def bp(name):
    return unreal.load_asset("/Game/Blocks/" + name).generated_class()


def spawn(cls, x, y=0.0, z=0.0, yaw=0.0, label=None, **props):
    a = actors.spawn_actor_from_class(cls, unreal.Vector(x, y, z), unreal.Rotator(0.0, 0.0, yaw))
    for k, v in props.items():
        a.set_editor_property(k, v)  # editor property change re-runs construction
    if label:
        a.set_actor_label(label)
    return a


def block(name, x, y=0, z=0, **props):
    return spawn(bp(name), x, y, z, **props)


def strip(name, x0, x1, z, lanes=LANES3, step=100):
    """A strip of blocks along X from x0 to x1 inclusive."""
    for x in range(x0, x1 + 1, step):
        for y in lanes:
            block(name, x, y, z)


def coins(points, z_above_top=60):
    """Coins at (x, y, top) points, hovering above a block top."""
    for x, y, top in points:
        block("BP_Coin", x, y, top + z_above_top)


def prop(mesh_path, x, y, z, scale=1.0, yaw=0.0, label=None):
    """Decoration mesh. spawn_actor_from_object needs editor UI, so spawn a StaticMeshActor."""
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z),
                                      unreal.Rotator(0.0, 0.0, yaw))
    a.static_mesh_component.set_static_mesh(unreal.load_asset(mesh_path))
    a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    if label:
        a.set_actor_label(label)
    return a


def sky_and_light(sun_pitch=-50.0, sun_yaw=35.0):
    spawn(unreal.DirectionalLight, 0, 0, 2000, label="Sun").set_actor_rotation(
        unreal.Rotator(-15.0, sun_pitch, sun_yaw), False)  # roll, pitch, yaw
    sky = spawn(unreal.SkyLight, 0, 0, 1000, label="SkyLight")
    sky.light_component.set_editor_property("real_time_capture", True)
    spawn(unreal.SkyAtmosphere, 0, 0, 0, label="SkyAtmosphere")
    spawn(unreal.ExponentialHeightFog, 0, 0, -600, label="Fog")


def use_platforming_game_mode():
    """Our game mode: the template's platforming character plus the HUD."""
    world = editor.get_editor_world()
    world.get_world_settings().set_editor_property(
        "default_game_mode", unreal.load_asset("/Game/Game/BP_PlatformerGameMode").generated_class())


def save():
    levels.save_current_level()
    return len(actors.get_all_level_actors())
