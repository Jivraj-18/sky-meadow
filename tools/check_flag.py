import unreal
m = unreal.load_asset("/Game/Kit/Kenney/flag"); b = m.get_bounding_box(); print("CHK flag", b.max - b.min)
f = unreal.load_asset("/Game/Kit/Level/Flag"); print("CHK Flag material", type(f).__name__, f.get_editor_property("two_sided") if isinstance(f, unreal.Material) else f.get_editor_property("base_property_overrides").get_editor_property("two_sided"))
