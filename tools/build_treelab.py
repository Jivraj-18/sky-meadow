"""Build /Game/Maps/Lvl_TreeLab: an empty test world with a lineup of trees, simple to complex.

Lineup along +X: cartoon kit tree, then the Procedural Vegetation Editor samples
(Common Hazel 0.9-4.7 m, Quaking Aspen 4.5-14 m). Stress forests are added by tools/treelab_stress.py.
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.expanduser("~/unreal-tests/tools"))
import levelkit as lk  # noqa: E402
importlib.reload(lk)
import unreal  # noqa: E402

LEVEL = "/Game/Maps/Lvl_TreeLab"
PVE = "/ProceduralVegetationEditor/SampleAssets/"
lib = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary

# Ground material: plain earthy green, fully rough.
MAT = "/Game/TreeLab/M_LabGround"
if not lib.does_asset_exist(MAT):
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_LabGround", "/Game/TreeLab", unreal.Material, unreal.MaterialFactoryNew())
    color = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
    color.set_editor_property("constant", unreal.LinearColor(0.09, 0.13, 0.05, 1.0))
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 200)
    rough.set_editor_property("r", 0.95)
    mel.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    lib.save_loaded_asset(mat, only_if_is_dirty=False)

lk.new_level(LEVEL)
lk.sky_and_light(sun_pitch=-35.0, sun_yaw=-60.0)

ground = lk.prop("/Engine/BasicShapes/Plane", 0, 0, 0, 1.0, label="Ground")
ground.set_actor_scale3d(unreal.Vector(400, 400, 1))  # 400 m x 400 m
ground.static_mesh_component.set_material(0, unreal.load_asset(MAT))

# Lineup: (label, asset, x position)
LINEUP = [
    ("Cartoon kit tree", "/Game/Kit/Nature/Tree", 0),
    ("Hazel 4 (0.9 m)", PVE + "Tree_Common_Hazel_01/SK_CommonHazel_04", 600),
    ("Hazel 3 (1.7 m)", PVE + "Tree_Common_Hazel_01/SK_CommonHazel_03", 1100),
    ("Hazel 2 (2.9 m)", PVE + "Tree_Common_Hazel_01/SK_CommonHazel_02", 1700),
    ("Hazel 1 (4.7 m)", PVE + "Tree_Common_Hazel_01/SK_CommonHazel_01", 2500),
    ("Aspen 4 (4.5 m)", PVE + "Tree_European_QuakingAspen_01/SK_European_QuakingAspen_04", 3500),
    ("Aspen 3 (7.1 m)", PVE + "Tree_European_QuakingAspen_01/SK_European_QuakingAspen_03", 4600),
    ("Aspen 2 (10.4 m)", PVE + "Tree_European_QuakingAspen_01/SK_European_QuakingAspen_02", 6000),
    ("Aspen 1 (14 m)", PVE + "Tree_European_QuakingAspen_01/SK_European_QuakingAspen_01", 7800),
]
for label, asset, x in LINEUP:
    mesh = unreal.load_asset(asset)
    if isinstance(mesh, unreal.StaticMesh):
        lk.prop(asset, x, 0, 0, 0.5, label=label)
    else:
        a = lk.actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(x, 0, 0))
        a.skeletal_mesh_component.set_skinned_asset_and_update(mesh)
        a.set_actor_label(label)
    text = lk.actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(x, -350, 20),
                                            unreal.Rotator(0, 0, 90))
    tr = text.text_render
    tr.set_editor_property("text", label)
    tr.set_editor_property("world_size", 40.0)
    tr.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    text.set_actor_label("Label " + label)

print("TREELAB BUILT", lk.save(), "actors")
