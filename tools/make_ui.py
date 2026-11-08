"""Create the HUD assets: icon textures, WBP_HUD, BP_PlatformerHUD and BP_PlatformerGameMode.

BP_PlatformerGameMode extends the template's platforming game mode and adds our HUD; levels use
it. Re-running updates everything in place.
"""
import os

import unreal

ICONS = os.path.expanduser("~/unreal-tests/assets_src/ui")
lib = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()

LEVEL_TITLES = {"Lvl_World1_1": "WORLD 1-1\nSKY MEADOW"}


def import_icon(name):
    path = "/Game/UI/" + name
    params = unreal.ImportAssetParameters()
    params.is_automated = True
    params.replace_existing = True
    source = unreal.InterchangeManager.create_source_data(os.path.join(ICONS, name + ".png"))
    unreal.InterchangeManager.get_interchange_manager_scripted().import_asset("/Game/UI", source, params)
    tex = unreal.load_asset(path)
    tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
    tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    lib.save_loaded_asset(tex, only_if_is_dirty=False)
    return tex


def blueprint(path, parent, factory_cls=unreal.BlueprintFactory, asset_cls=unreal.Blueprint):
    if lib.does_asset_exist(path):
        return unreal.load_asset(path)
    factory = factory_cls()
    factory.set_editor_property("parent_class", parent)
    folder, name = path.rsplit("/", 1)
    return tools.create_asset(name, folder, asset_cls, factory)


def finish(bp, **props):
    cdo = unreal.get_default_object(bp.generated_class())
    for k, v in props.items():
        cdo.set_editor_property(k, v)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    lib.save_loaded_asset(bp, only_if_is_dirty=False)
    return bp


icons = {n: import_icon(n) for n in ("T_HeartFull", "T_HeartEmpty", "T_Coin")}

wbp = blueprint("/Game/UI/WBP_HUD", unreal.PlatformerHUDWidget,
                unreal.WidgetBlueprintFactory, unreal.WidgetBlueprint)
finish(wbp, heart_full_icon=icons["T_HeartFull"], heart_empty_icon=icons["T_HeartEmpty"],
       coin_icon=icons["T_Coin"], level_titles={k: unreal.Text(v) for k, v in LEVEL_TITLES.items()})

hud = finish(blueprint("/Game/UI/BP_PlatformerHUD", unreal.PlatformerHUD), widget_class=wbp.generated_class())

template_gm = unreal.load_asset("/Game/Variant_Platforming/Blueprints/BP_PlatformingGameMode").generated_class()
gm = finish(blueprint("/Game/Game/BP_PlatformerGameMode", template_gm), hud_class=hud.generated_class())

print("UI DONE", wbp.get_path_name(), hud.get_path_name(), gm.get_path_name())
