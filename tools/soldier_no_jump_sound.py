"""Soldier: no jump sound (the blue platformer character keeps it)."""
import unreal

bp = unreal.load_asset("/Game/Soldier/BP_SoldierCharacter")
subs = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib_sub = unreal.SubobjectDataBlueprintFunctionLibrary
for h in subs.k2_gather_subobject_data_for_blueprint(bp):
    obj = lib_sub.get_object(lib_sub.get_data(h))
    if isinstance(obj, unreal.KitCharacterAnimator):
        obj.set_editor_property("play_jump_sound", False)
        print("JUMPSOUND", obj.get_editor_property("play_jump_sound"))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
