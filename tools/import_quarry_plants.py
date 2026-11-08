"""Import the free (CC0) Poly Haven conifers and meadow plants into /Game/Quarry/Plants.

Trees get Nanite (the fir is film-detail geometry); alpha-blended plant materials are switched
to the masked glTF parent (cut-out grass, like games use).
"""
import os

import unreal

SRC = os.path.expanduser("~/unreal-tests/assets_src/polyhaven")
DEST = "/Game/Quarry/Plants/"
lib = unreal.EditorAssetLibrary
manager = unreal.InterchangeManager.get_interchange_manager_scripted()
MASK_PARENT = unreal.load_asset("/InterchangeAssets/gltf/MaterialInstances/MI_Default_Mask_DS")
TREES = ("fir_tree_01", "pine_sapling_small", "fir_sapling")
PLANTS = ("grass_medium_02", "grass_bermuda_01", "dandelion_01", "celandine_01", "weed_plant_02", "shrub_03", "fern_02")

for name in TREES + PLANTS:
    folder = os.path.join(SRC, name)
    src = [f for f in os.listdir(folder) if f.endswith((".gltf", ".fbx"))][0]
    params = unreal.ImportAssetParameters()
    params.is_automated = True
    params.replace_existing = True
    try:
        manager.import_asset(DEST + name, unreal.InterchangeManager.create_source_data(os.path.join(folder, src)), params)
    except RuntimeError as exc:
        unreal.log_warning("import %s: %s" % (name, exc))

for path in lib.list_assets(DEST, recursive=True, include_folder=False):
    asset = unreal.load_asset(path)
    if isinstance(asset, unreal.MaterialInstanceConstant):
        parent = asset.get_editor_property("parent")
        if parent and "Blend" in parent.get_name() and MASK_PARENT:
            asset.set_editor_property("parent", MASK_PARENT)
            lib.save_loaded_asset(asset, only_if_is_dirty=False)
    elif isinstance(asset, unreal.StaticMesh) and any("/%s/" % t in path for t in TREES):
        nanite = asset.get_editor_property("nanite_settings")
        nanite.set_editor_property("enabled", True)
        asset.set_editor_property("nanite_settings", nanite)
        lib.save_loaded_asset(asset, only_if_is_dirty=False)

lib.save_directory(DEST, only_if_is_dirty=False, recursive=True)
for path in sorted(lib.list_assets(DEST, recursive=True, include_folder=False)):
    asset = unreal.load_asset(path)
    if isinstance(asset, unreal.StaticMesh):
        b = asset.get_bounding_box()
        print("QP %-60s size_cm=%s tris=%d nanite=%s" % (path.split(DEST)[1].split(".")[0],
              [round(v) for v in (b.max - b.min).to_tuple()], asset.get_num_triangles(0),
              asset.get_editor_property("nanite_settings").get_editor_property("enabled")))
