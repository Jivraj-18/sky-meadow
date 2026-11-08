"""Create the burst effect Blueprints (/Game/Effects) and point Platformer Effects settings at them."""
import configparser
import os

import unreal

GAME_INI = os.path.expanduser("~/unreal-tests/RealWorldGame/Config/DefaultGame.ini")
lib = unreal.EditorAssetLibrary
V2 = unreal.Vector2D

# name: (settings slot, mesh, {properties})
EFFECTS = {
    "BP_FX_Coin": ("CoinCollect", "/Game/Kit/Pickups/Star",
                   dict(count=10, lifetime=0.6, speed=V2(220, 420), up_bias=0.5, gravity=500.0,
                        start_scale=0.2, spin=540.0, drag=1.5)),
    "BP_FX_Stomp": ("Stomp", "/Game/Kit/Nature/Cloud_1",
                    dict(count=8, lifetime=0.45, speed=V2(250, 400), up_bias=0.15, gravity=0.0,
                         start_scale=0.2, spin=90.0, drag=4.0)),
    "BP_FX_Land": ("Land", "/Game/Kit/Nature/Cloud_2",
                   dict(count=7, lifetime=0.4, speed=V2(170, 280), up_bias=0.05, gravity=0.0,
                        start_scale=0.13, spin=60.0, drag=5.0)),
    "BP_FX_Checkpoint": ("Checkpoint", "/Game/Kit/Pickups/Star",
                         dict(count=16, lifetime=1.0, speed=V2(300, 550), up_bias=0.8, gravity=700.0,
                              start_scale=0.25, spin=540.0, drag=1.0)),
    "BP_FX_JumpPad": ("JumpPad", "/Game/Kit/Nature/Cloud_3",
                      dict(count=8, lifetime=0.4, speed=V2(200, 300), up_bias=0.0, gravity=0.0,
                           start_scale=0.15, spin=60.0, drag=4.0)),
    "BP_FX_Hurt": ("Hurt", "/Game/Kit/Pickups/Heart",
                   dict(count=5, lifetime=0.6, speed=V2(150, 300), up_bias=0.8, gravity=600.0,
                        start_scale=0.2, spin=180.0, drag=1.0)),
}

slots = {}
for name, (slot, mesh, props) in EFFECTS.items():
    path = "/Game/Effects/" + name
    if lib.does_asset_exist(path):
        bp = unreal.load_asset(path)
    else:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", unreal.KitEffect)
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Effects", unreal.Blueprint, factory)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("piece_mesh", unreal.load_asset(mesh))
    for k, v in props.items():
        cdo.set_editor_property(k, v)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    lib.save_loaded_asset(bp, only_if_is_dirty=False)
    slots[slot] = "/Game/Effects/%s.%s_C" % (name, name)

ini = configparser.RawConfigParser(strict=False)
ini.optionxform = str
ini.read(GAME_INI)
section = "/Script/RealWorldGame.PlatformerEffectsSettings"
if not ini.has_section(section):
    ini.add_section(section)
for slot, cls in slots.items():
    ini.set(section, slot, cls)
with open(GAME_INI, "w") as fh:
    ini.write(fh, space_around_delimiters=False)
print("EFFECTS DONE", slots)
