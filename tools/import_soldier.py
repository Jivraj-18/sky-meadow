"""Import the Mixamo "Swat" soldier + animations and make it the quarry's player character.

Mixamo (Adobe) characters/animations are free and royalty-free for projects; raw files must not
be redistributed on their own. Animations were downloaded "Without Skin" (and "In Place" for
walk/run) and are imported onto the Swat skeleton.

Creates /Game/Soldier/BP_SoldierCharacter (platforming character + KitCharacterAnimator using the
soldier) and BP_QuarryGameMode, and sets Lvl_Quarry to use it. Other levels keep the blue character.
"""
import os

import unreal

SRC = os.path.expanduser("~/unreal-tests/assets_src/mixamo")
DEST = "/Game/Soldier"
lib = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
manager = unreal.InterchangeManager.get_interchange_manager_scripted()
ANIMS = {"idle": "Breathing Idle", "walk": "Standard Walk", "run": "Standard Run", "jump_start": "Jump",
         "air": "Falling Idle", "land": "Falling To Landing", "hurt": "Hit Reaction", "lose": "Falling Back Death",
         "win": "Waving"}


def interchange(path, dest, pipeline=None):
    params = unreal.ImportAssetParameters()
    params.is_automated = True
    params.replace_existing = True
    if pipeline:
        params.override_pipelines = [pipeline]
    try:
        manager.import_asset(dest, unreal.InterchangeManager.create_source_data(path), params)
    except RuntimeError as exc:
        unreal.log_warning("import %s: %s" % (path, exc))


def find(folder, cls):
    for p in lib.list_assets(folder, recursive=True, include_folder=False):
        a = unreal.load_asset(p)
        if isinstance(a, cls):
            return a
    return None


# 1 Character mesh (+ skeleton, physics asset, materials).
if not lib.does_directory_exist(DEST + "/Mesh") or find(DEST + "/Mesh", unreal.SkeletalMesh) is None:
    interchange(os.path.join(SRC, "Swat.fbx"), DEST + "/Mesh")
mesh = find(DEST + "/Mesh", unreal.SkeletalMesh)
skeleton = mesh.get_editor_property("skeleton")
print("SOLDIER mesh", mesh.get_path_name(), "skeleton", skeleton.get_name())

# 2 Animations onto that skeleton. (Interchange's pipeline override can't be passed from Python,
#   so use the FBX import options, which Unreal converts for Interchange.)
anims = {}
tasks = []
for slot, name in ANIMS.items():
    opts = unreal.FbxImportUI()
    opts.set_editor_property("import_mesh", False)
    opts.set_editor_property("import_animations", True)
    opts.set_editor_property("import_as_skeletal", True)
    opts.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    opts.set_editor_property("skeleton", skeleton)
    t = unreal.AssetImportTask()
    t.filename = os.path.join(SRC, name + ".fbx")
    t.destination_path = DEST + "/Anims/" + name.replace(" ", "_")
    t.automated = True
    t.replace_existing = True
    t.save = True
    t.options = opts
    tasks.append((slot, t))
tools.import_asset_tasks([t for _, t in tasks])
for slot, t in tasks:
    anims[slot] = find(t.destination_path, unreal.AnimSequence)
    print("SOLDIER anim", slot, anims[slot].get_path_name() if anims[slot] else None,
          anims[slot].get_editor_property("skeleton").get_name() if anims[slot] else "")


def blueprint(path, parent):
    if lib.does_asset_exist(path):
        return unreal.load_asset(path)
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", parent)
    folder, name = path.rsplit("/", 1)
    return tools.create_asset(name, folder, unreal.Blueprint, f)


# 3 Player character: the platforming character with the animator pointed at the soldier.
bp = blueprint(DEST + "/BP_SoldierCharacter",
               unreal.load_asset("/Game/Variant_Platforming/Blueprints/BP_PlatformingCharacter").generated_class())
subs = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib_sub = unreal.SubobjectDataBlueprintFunctionLibrary
handles = subs.k2_gather_subobject_data_for_blueprint(bp)
animator = None
for h in handles:
    obj = lib_sub.get_object(lib_sub.get_data(h))
    if isinstance(obj, unreal.KitCharacterAnimator):
        animator = obj
if animator is None:
    handle, _ = subs.add_new_subobject(unreal.AddNewSubobjectParams(
        parent_handle=handles[0], new_class=unreal.KitCharacterAnimator, blueprint_context=bp))
    animator = lib_sub.get_object(lib_sub.get_data(handle))
animator.set_editor_property("visual_mesh", mesh)
animator.set_editor_property("visual_height", 180.0)
for slot, anim in anims.items():
    if anim:
        animator.set_editor_property(slot, anim)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
lib.save_loaded_asset(bp, only_if_is_dirty=False)

# 4 Game mode for the quarry: same as the platformer's, but spawns the soldier.
gm = blueprint(DEST + "/BP_QuarryGameMode", unreal.load_asset("/Game/Game/BP_PlatformerGameMode").generated_class())
unreal.get_default_object(gm.generated_class()).set_editor_property("default_pawn_class", bp.generated_class())
unreal.BlueprintEditorLibrary.compile_blueprint(gm)
lib.save_loaded_asset(gm, only_if_is_dirty=False)

# 5 Point only the quarry level at it.
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if ues.get_editor_world().get_name() != "Lvl_Quarry":
    levels.load_level("/Game/Maps/Lvl_Quarry")
ues.get_editor_world().get_world_settings().set_editor_property("default_game_mode", gm.generated_class())
levels.save_current_level()
lib.save_directory(DEST, only_if_is_dirty=False, recursive=True)
b = mesh.get_bounds()
print("SOLDIER DONE height_cm=%.0f anims=%d" % (b.box_extent.z * 2, sum(1 for a in anims.values() if a)))
