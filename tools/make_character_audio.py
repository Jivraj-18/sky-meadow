"""Import sounds, configure Platformer Audio, and create BP_PlayerCharacter (kit look).

Run in the live editor (tools/ue.py): sound import goes through AssetTools, which needs editor UI.
"""
import configparser
import os

import unreal

AUDIO_SRC = os.path.expanduser("~/unreal-tests/assets_src/audio")
GAME_INI = os.path.expanduser("~/unreal-tests/RealWorldGame/Config/DefaultGame.ini")
CHAR = "/Game/Kit/Character/Character/"
ARM = CHAR + "CharacterCharacterArmature_"
lib = unreal.EditorAssetLibrary

# 1 Sounds ------------------------------------------------------------------------------------
tasks = []
for f in sorted(os.listdir(AUDIO_SRC)):
    if f.endswith(".wav"):
        t = unreal.AssetImportTask()
        t.filename = os.path.join(AUDIO_SRC, f)
        t.destination_path = "/Game/Audio"
        t.automated = True
        t.replace_existing = True
        t.save = True
        tasks.append(t)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
music = unreal.load_asset("/Game/Audio/MUS_SkyMeadow")
music.set_editor_property("looping", True)
lib.save_loaded_asset(music, only_if_is_dirty=False)
print("sounds:", [os.path.basename(t.filename) for t in tasks if t.imported_object_paths])

# 2 Project Settings > Platformer Audio, written to DefaultGame.ini (loaded at editor start) -----
SOUNDS = {"Jump": "SFX_Jump", "Coin": "SFX_Coin", "Stomp": "SFX_Stomp", "Hurt": "SFX_Hurt",
          "JumpPad": "SFX_JumpPad", "Checkpoint": "SFX_Checkpoint", "LevelComplete": "SFX_LevelComplete",
          "GameOver": "SFX_GameOver", "LevelMusic": "MUS_SkyMeadow"}
ini = configparser.RawConfigParser(strict=False)
ini.optionxform = str
ini.read(GAME_INI)
section = "/Script/RealWorldGame.PlatformerAudioSettings"
if not ini.has_section(section):
    ini.add_section(section)
for prop, asset in SOUNDS.items():
    ini.set(section, prop, "/Game/Audio/%s.%s" % (asset, asset))
with open(GAME_INI, "w") as fh:
    ini.write(fh, space_around_delimiters=False)

# 3 BP_PlayerCharacter: platforming character + kit look --------------------------------------
path = "/Game/Game/BP_PlayerCharacter"
if lib.does_asset_exist(path):
    bp = unreal.load_asset(path)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property(
        "parent_class",
        unreal.load_asset("/Game/Variant_Platforming/Blueprints/BP_PlatformingCharacter").generated_class())
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_PlayerCharacter", "/Game/Game", unreal.Blueprint, factory)

subs = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles = subs.k2_gather_subobject_data_for_blueprint(bp)
lib_sub = unreal.SubobjectDataBlueprintFunctionLibrary
animator = None
for h in handles:
    obj = lib_sub.get_object(lib_sub.get_data(h))
    if isinstance(obj, unreal.KitCharacterAnimator):
        animator = obj
if animator is None:
    params = unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=unreal.KitCharacterAnimator,
                                          blueprint_context=bp)
    handle, fail = subs.add_new_subobject(params)
    animator = lib_sub.get_object(lib_sub.get_data(handle))

# Python names drop the "In" of InAir -> "air".
anims = {"idle": "Idle", "walk": "Walk", "run": "Run", "jump_start": "Jump", "air": "Jump_Idle",
         "land": "Jump_Land", "hurt": "HitReact", "win": "Wave", "lose": "Death"}
animator.set_editor_property("visual_mesh", unreal.load_asset(CHAR + "Character"))
for prop, anim in anims.items():
    animator.set_editor_property(prop, unreal.load_asset(ARM + anim))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
lib.save_loaded_asset(bp, only_if_is_dirty=False)

# 4 Game mode spawns our character -------------------------------------------------------------
gm = unreal.load_asset("/Game/Game/BP_PlatformerGameMode")
unreal.get_default_object(gm.generated_class()).set_editor_property("default_pawn_class", bp.generated_class())
unreal.BlueprintEditorLibrary.compile_blueprint(gm)
lib.save_loaded_asset(gm, only_if_is_dirty=False)

print("CHARACTER+AUDIO DONE", animator.get_editor_property("visual_mesh").get_name(),
      {p: animator.get_editor_property(p).get_name() for p in anims})
