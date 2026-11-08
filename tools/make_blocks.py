"""Create the drag-and-drop building block Blueprints in /Game/Blocks.

Each Blueprint subclasses a C++ block (KitBlock, MovingPlatform, CoinPickup...) and only
sets the look and defaults, so they stay editable in the Details panel.
Re-running updates existing Blueprints in place.
"""
import os

import unreal

KENNEY_DIR = os.path.expanduser("~/unreal-tests/assets_src/kenney_platformer/Models/FBX format")
KENNEY_MODELS = ["spring", "flag"]

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
lib = unreal.EditorAssetLibrary


def import_kenney_models():
    dest = "/Game/Kit/Kenney"
    for name in KENNEY_MODELS:
        if lib.does_asset_exist(dest + "/" + name):
            continue
        params = unreal.ImportAssetParameters()
        params.is_automated = True
        params.replace_existing = True
        source = unreal.InterchangeManager.create_source_data(os.path.join(KENNEY_DIR, name + ".fbx"))
        unreal.InterchangeManager.get_interchange_manager_scripted().import_asset(dest, source, params)
        m = unreal.load_asset(dest + "/" + name)
        if isinstance(m, unreal.StaticMesh):  # imports come without collision
            m.get_editor_property("body_setup").set_editor_property(
                "collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            lib.save_loaded_asset(m, only_if_is_dirty=False)


def make_two_sided(path):
    """Thin cloth (flags) is single-sided and vanishes when seen from behind."""
    mat = unreal.load_asset(path)
    if isinstance(mat, unreal.Material):
        mat.set_editor_property("two_sided", True)
        unreal.MaterialEditingLibrary.recompile_material(mat)
    else:
        overrides = mat.get_editor_property("base_property_overrides")
        overrides.set_editor_property("override_two_sided", True)
        overrides.set_editor_property("two_sided", True)
        mat.set_editor_property("base_property_overrides", overrides)
    lib.save_loaded_asset(mat, only_if_is_dirty=False)


def mesh(path):
    m = unreal.load_asset(path)
    if m is None:
        raise RuntimeError("missing mesh " + path)
    return m


# name: (parent C++ class, {property: value})
BLOCKS = {
    "BP_GrassBlock": (unreal.KitBlock, {"mesh_asset": "/Game/Kit/Cubes/Cube_Grass_Single"}),
    "BP_DirtBlock": (unreal.KitBlock, {"mesh_asset": "/Game/Kit/Cubes/Cube_Dirt_Single"}),
    "BP_BrickBlock": (unreal.KitBlock, {"mesh_asset": "/Game/Kit/Cubes/Cube_Bricks"}),
    "BP_QuestionBlock": (unreal.KitBlock, {"mesh_asset": "/Game/Kit/Cubes/Cube_Question"}),
    "BP_Crate": (unreal.KitBlock, {"mesh_asset": "/Game/Kit/Cubes/Cube_Crate"}),
    "BP_RockPlatform": (unreal.KitBlock, {"mesh_asset": "/Game/Kit/Nature/RockPlatforms_Medium"}),
    "BP_Bridge": (unreal.KitBlock, {"mesh_asset": "/Game/Kit/Level/Bridge_Small"}),
    "BP_MovingPlatform": (unreal.MovingPlatform, {"mesh_asset": "/Game/Kit/Cubes/Cube_Grass_Single",
                                                  "kit_scale": 0.9}),
    "BP_Coin": (unreal.CoinPickup, {"mesh_asset": "/Game/Kit/Pickups/Coin"}),
    "BP_JumpPad": (unreal.JumpPad, {"mesh_asset": "/Game/Kit/Kenney/spring", "kit_scale": 1.0}),
    "BP_GoalFlag": (unreal.GoalFlag, {"mesh_asset": "/Game/Kit/Level/Goal_Flag", "kit_scale": 0.75}),
    "BP_KillZone": (unreal.KillZone, {}),
    "BP_Checkpoint": (unreal.Checkpoint, {"mesh_asset": "/Game/Kit/Kenney/flag", "kit_scale": 1.5}),
}


def enemy(kind, move, extent, **extra):
    base = "/Game/Kit/Enemies/%s/" % kind
    arm = "%sMonsterArmature_" % kind
    props = {"mesh_asset": base + kind, "move_anim": base + arm + move,
             "death_anim": base + arm + "Death", "body_extent": unreal.Vector(*extent)}
    props.update(extra)
    return (unreal.KitEnemy, props)


ENEMIES = {
    "BP_Crab": enemy("Crab", "Walk", (55, 40, 35)),
    "BP_Skull": enemy("Skull", "Walk", (35, 35, 37), speed=200.0),
    "BP_Monster": enemy("Enemy", "Walk", (45, 35, 41), speed=120.0),
    "BP_Bee": enemy("Bee", "Flying", (45, 35, 35), speed=180.0),
}
BLOCKS.update(ENEMIES)

import_kenney_models()
make_two_sided("/Game/Kit/Level/Flag")

for name, (parent, props) in BLOCKS.items():
    path = "/Game/Blocks/" + name
    if lib.does_asset_exist(path):
        bp = unreal.load_asset(path)
    else:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", parent)
        bp = asset_tools.create_asset(name, "/Game/Blocks", unreal.Blueprint, factory)
    cdo = unreal.get_default_object(bp.generated_class())
    for prop, value in props.items():
        if isinstance(value, str) and value.startswith("/Game/"):
            value = mesh(value)  # any asset path: mesh, animation...
        cdo.set_editor_property(prop, value)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    lib.save_loaded_asset(bp, only_if_is_dirty=False)
    print("block", name, "parent", parent.__name__, props)

lib.save_directory("/Game/Kit/Kenney", only_if_is_dirty=False)
print("BLOCKS DONE", len(BLOCKS))
