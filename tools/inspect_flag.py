import unreal
for p in ["/Game/Kit/Level/Goal_Flag", "/Game/Kit/Level/Tower", "/Game/Kit/Level/Arrow_Up"]:
    m = unreal.load_asset(p)
    print("FLAG", p, "sections:", m.get_num_sections(0), "lods:", m.get_num_lods())
    for i, sm in enumerate(m.static_materials):
        mi = sm.material_interface
        print("FLAG   slot", i, sm.material_slot_name, mi.get_path_name() if mi else None)
for a in unreal.EditorAssetLibrary.list_assets("/Game/Kit/Level", recursive=False):
    if "Flag" in a or "flag" in a:
        print("FLAG asset", a)
