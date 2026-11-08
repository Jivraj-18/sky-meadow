import unreal
for a in unreal.EditorAssetLibrary.list_assets("/Game/Blocks", recursive=False):
    bp = unreal.load_asset(a)
    if not isinstance(bp, unreal.Blueprint):
        continue
    cdo = unreal.get_default_object(bp.generated_class())
    m = cdo.get_editor_property("mesh_asset") if hasattr(cdo, "mesh_asset") else None
    print("CHK", bp.get_name(), m.get_name() if m else None, cdo.get_editor_property("kit_scale") if hasattr(cdo, "kit_scale") else "-")
s = unreal.load_asset("/Game/Kit/Kenney/spring")
b = s.get_bounding_box(); print("CHK spring size", b.max - b.min)
