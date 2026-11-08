"""Import the Poly Haven (CC0) textures and models for the quarry scene into /Game/Quarry."""
import os

import unreal

SRC = os.path.expanduser("~/unreal-tests/assets_src/polyhaven")
lib = unreal.EditorAssetLibrary
manager = unreal.InterchangeManager.get_interchange_manager_scripted()


def interchange(path, dest):
    params = unreal.ImportAssetParameters()
    params.is_automated = True
    params.replace_existing = True
    try:
        return manager.import_asset(dest, unreal.InterchangeManager.create_source_data(path), params)
    except RuntimeError as exc:
        unreal.log_warning("import %s: %s" % (path, exc))
        return False


# Ground textures: normal maps are OpenGL-style (green up) -> flip for Unreal; masks are linear.
for tex_set in ("rock_face_03", "aerial_grass_rock"):
    folder = os.path.join(SRC, tex_set)
    for f in sorted(os.listdir(folder)):
        interchange(os.path.join(folder, f), "/Game/Quarry/Textures")
        asset = unreal.load_asset("/Game/Quarry/Textures/" + os.path.splitext(f)[0])
        if asset is None:
            continue
        if "_nor_gl" in f:
            asset.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            asset.set_editor_property("flip_green_channel", True)
            asset.set_editor_property("srgb", False)
        elif "_rough" in f or "_arm" in f:
            asset.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
            asset.set_editor_property("srgb", False)
        lib.save_loaded_asset(asset, only_if_is_dirty=False)

# Models (glTF): each into its own folder.
for model in ("boulder_01", "namaqualand_boulder_02", "rock_moss_set_01", "grass_medium_01"):
    gltf = [f for f in os.listdir(os.path.join(SRC, model)) if f.endswith(".gltf")][0]
    interchange(os.path.join(SRC, model, gltf), "/Game/Quarry/" + model)

lib.save_directory("/Game/Quarry", only_if_is_dirty=False, recursive=True)
for path in sorted(lib.list_assets("/Game/Quarry", recursive=True, include_folder=False)):
    data = lib.find_asset_data(path)
    cls = str(data.asset_class_path.asset_name)
    extra = ""
    if cls == "StaticMesh":
        m = unreal.load_asset(path)
        b = m.get_bounding_box()
        extra = "size_cm=%s mats=%s" % ([round(v) for v in (b.max - b.min).to_tuple()],
                                       [s.material_interface.get_name() if s.material_interface else None for s in m.static_materials])
    elif cls in ("MaterialInstanceConstant", "Material"):
        mi = unreal.load_asset(path)
        parent = mi.get_editor_property("parent").get_name() if cls == "MaterialInstanceConstant" and mi.get_editor_property("parent") else "-"
        extra = "parent=%s blend=%s" % (parent, mi.get_editor_property("blend_mode") if cls == "Material" else
                                        mi.get_editor_property("base_property_overrides").get_editor_property("blend_mode"))
    print("QA %-22s %-34s %s" % (cls, path.split("/Game/Quarry/")[1].split(".")[0], extra))
