"""Inventory of the Procedural Vegetation Editor sample assets (types, triangle counts, Nanite)."""
import unreal

lib = unreal.EditorAssetLibrary
ROOT = "/ProceduralVegetationEditor/SampleAssets"
from collections import Counter

classes = Counter()
for path in lib.list_assets(ROOT, recursive=True, include_folder=False):
    data = lib.find_asset_data(path)
    cls = str(data.asset_class_path.asset_name)
    classes[cls] += 1
    name = str(data.asset_name)
    if cls == "SkeletalMesh" and name.startswith("SK_") and "/Instances/" not in path:
        m = unreal.load_asset(path)
        b = m.get_bounds()
        nanite = m.get_editor_property("nanite_settings").get_editor_property("enabled") if hasattr(m, "nanite_settings") else "?"
        print("TREE", name, "height_cm=%.0f" % (b.box_extent.z * 2), "nanite=%s" % nanite,
              "materials=%d" % len(m.materials), path)
    elif cls == "StaticMesh" and "/Instances/" in path and name.startswith(("BrLeaf_000", "CH_Branch_A")):
        m = unreal.load_asset(path)
        print("PART", name, "tris=%d" % m.get_num_triangles(0), path)
    elif cls in ("ProceduralVegetation", "ProceduralVegetationPreset", "World", "PCGGraph"):
        print(cls.upper(), name, path)
print("CLASSES", dict(classes))
