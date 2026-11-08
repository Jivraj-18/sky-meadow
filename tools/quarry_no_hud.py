"""Quarry: no on-screen stats. A HUD without a widget keeps the R/Esc keys but shows nothing."""
import unreal

lib = unreal.EditorAssetLibrary
path = "/Game/Soldier/BP_QuarryHUD"
if lib.does_asset_exist(path):
    hud = unreal.load_asset(path)
else:
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", unreal.PlatformerHUD)
    hud = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_QuarryHUD", "/Game/Soldier", unreal.Blueprint, f)
unreal.get_default_object(hud.generated_class()).set_editor_property("widget_class", None)
unreal.BlueprintEditorLibrary.compile_blueprint(hud)
lib.save_loaded_asset(hud, only_if_is_dirty=False)

gm = unreal.load_asset("/Game/Soldier/BP_QuarryGameMode")
unreal.get_default_object(gm.generated_class()).set_editor_property("hud_class", hud.generated_class())
unreal.BlueprintEditorLibrary.compile_blueprint(gm)
lib.save_loaded_asset(gm, only_if_is_dirty=False)
print("NOHUD done", unreal.get_default_object(gm.generated_class()).get_editor_property("hud_class").get_name())
