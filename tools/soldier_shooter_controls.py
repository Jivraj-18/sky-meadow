"""Give the soldier BGMI-style controls: ShooterControls component (camera, one jump, sprint,
no dash) and animation speeds matched to the new run speed."""
import unreal

bp = unreal.load_asset("/Game/Soldier/BP_SoldierCharacter")
subs = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib_sub = unreal.SubobjectDataBlueprintFunctionLibrary
handles = subs.k2_gather_subobject_data_for_blueprint(bp)
controls = animator = None
for h in handles:
    obj = lib_sub.get_object(lib_sub.get_data(h))
    if isinstance(obj, unreal.ShooterControls):
        controls = obj
    elif isinstance(obj, unreal.KitCharacterAnimator):
        animator = obj
if controls is None:
    handle, _ = subs.add_new_subobject(unreal.AddNewSubobjectParams(
        parent_handle=handles[0], new_class=unreal.ShooterControls, blueprint_context=bp))
    controls = lib_sub.get_object(lib_sub.get_data(handle))

controls.set_editor_property("remove_mapping_contexts", [unreal.load_asset("/Game/Variant_Platforming/Input/IMC_Platforming")])
controls.set_editor_property("add_mapping_contexts", [unreal.load_asset("/Game/Input/IMC_Default")])

# Animations: walk below ~2.5 m/s, run above; the Mixamo run looks right at ~4.5 m/s.
animator.set_editor_property("run_speed", 250.0)
animator.set_editor_property("run_anim_speed", 450.0)
animator.set_editor_property("camera_lag_speed", 0.0)  # ShooterControls owns the camera now

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
print("SHOOTER controls", controls.get_editor_property("arm_length"), controls.get_editor_property("run_speed"),
      [c.get_name() for c in controls.get_editor_property("remove_mapping_contexts")],
      [c.get_name() for c in controls.get_editor_property("add_mapping_contexts")])
