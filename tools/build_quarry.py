"""Build /Game/Maps/Lvl_Quarry: a quarry-edge landscape modelled on the reference frame
(reference/cand_52.png, PUBG MOBILE trailer, CC BY 3.0) using only free assets:
Poly Haven CC0 textures/rocks/grass and the engine's Procedural Vegetation sample trees.

Everything is ordinary editable content: the Landscape (sculpt/paint brushes), every boulder and
tree as its own actor (move/rotate/delete), grass as Foliage instances (Foliage tool).
Run headless: tools/ue-headless.sh tools/build_quarry.py
"""
import importlib
import math
import os
import random
import sys

sys.path.insert(0, os.path.expanduser("~/unreal-tests/tools"))
import levelkit as lk  # noqa: E402
importlib.reload(lk)
import unreal  # noqa: E402

LEVEL = "/Game/Maps/Lvl_Quarry"
HEIGHTMAP = os.path.expanduser("~/unreal-tests/assets_src/terrain/quarry_505.r16")
Q = "/Game/Quarry/"
PVE = "/ProceduralVegetationEditor/SampleAssets/"
lib = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
random.seed(42)

# Quarry pit centre and rim radii (metres), matching tools/make_heightmap_quarry.py.
PIT_X, PIT_Y, RIM_RX, RIM_RY = 55.0, 10.0, 75.0, 55.0


# ---- Materials --------------------------------------------------------------------------------
def fix_grass_material():
    """Poly Haven grass is alpha-blended (glTF BLEND); switch to cut-out (masked) like game grass."""
    mi = unreal.load_asset(Q + "grass_medium_01/grass_medium_01_1k/Materials/grass_medium_01")
    # Plugin content isn't in the asset registry headless, so load the masked glTF parent by path.
    mask_parent = "/InterchangeAssets/gltf/MaterialInstances/MI_Default_Mask_DS"
    parent = unreal.load_asset(mask_parent)
    if parent:
        mi.set_editor_property("parent", parent)
    else:
        mask_parent = None
    lib.save_loaded_asset(mi, only_if_is_dirty=False)
    return mask_parent


def terrain_material():
    """Grass on flat ground, rock on slopes. Grass is projected from above; rock is triplanar so
    cliffs don't stretch. Tiling: grass 4 m, rock 6 m."""
    path = Q + "M_QuarryTerrain"
    if lib.does_asset_exist(path):
        lib.delete_asset(path)
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_QuarryTerrain", Q.rstrip("/"), unreal.Material, unreal.MaterialFactoryNew())
    tex = lambda n: unreal.load_asset(Q + "Textures/" + n)

    def node(cls, x, y, **props):
        e = mel.create_material_expression(mat, cls, x, y)
        for k, v in props.items():
            e.set_editor_property(k, v)
        return e

    # World-space UVs for the top-down grass projection.
    wp = node(unreal.MaterialExpressionWorldPosition, -1400, -200)
    xy = node(unreal.MaterialExpressionComponentMask, -1200, -200, r=True, g=True, b=False, a=False)
    mel.connect_material_expressions(wp, "", xy, "")
    uv = node(unreal.MaterialExpressionDivide, -1000, -200, const_b=400.0)
    mel.connect_material_expressions(xy, "", uv, "")

    grass_c = node(unreal.MaterialExpressionTextureSample, -700, -400, texture=tex("aerial_grass_rock_diff"))
    grass_n = node(unreal.MaterialExpressionTextureSample, -700, -150, texture=tex("aerial_grass_rock_nor_gl"),
                   sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    grass_r = node(unreal.MaterialExpressionTextureSample, -700, 100, texture=tex("aerial_grass_rock_rough"),
                   sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)  # texture uses TC_MASKS
    for s in (grass_c, grass_n, grass_r):
        mel.connect_material_expressions(uv, "", s, "UVs")

    # Rock: triplanar via the engine's WorldAlignedTexture function.
    rock_obj = node(unreal.MaterialExpressionTextureObject, -1000, 400, texture=tex("rock_face_03_diff"))
    rock_size = node(unreal.MaterialExpressionConstant3Vector, -1000, 600, constant=unreal.LinearColor(600, 600, 600, 0))
    rock = node(unreal.MaterialExpressionMaterialFunctionCall, -700, 400)
    rock.set_editor_property("material_function", unreal.load_asset(
        "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture"))
    mel.connect_material_expressions(rock_obj, "", rock, "TextureObject")
    mel.connect_material_expressions(rock_size, "", rock, "TextureSize")

    # Slope mask from the world-space normal: 1 on flat ground, 0 on cliffs.
    normal = node(unreal.MaterialExpressionVertexNormalWS, -1000, 800)
    nz = node(unreal.MaterialExpressionComponentMask, -800, 800, r=False, g=False, b=True, a=False)
    mel.connect_material_expressions(normal, "", nz, "")
    sub = node(unreal.MaterialExpressionSubtract, -600, 800, const_b=0.78)
    mel.connect_material_expressions(nz, "", sub, "")
    mul = node(unreal.MaterialExpressionMultiply, -450, 800, const_b=7.0)
    mel.connect_material_expressions(sub, "", mul, "")
    flat = node(unreal.MaterialExpressionSaturate, -300, 800)
    mel.connect_material_expressions(mul, "", flat, "")

    # Anti-tiling: average the grass at 4 m and 17 m, then vary brightness over ~120 m patches.
    uv2 = node(unreal.MaterialExpressionDivide, -1000, -600, const_b=1700.0)
    mel.connect_material_expressions(xy, "", uv2, "")
    grass_c2 = node(unreal.MaterialExpressionTextureSample, -700, -650, texture=tex("aerial_grass_rock_diff"))
    mel.connect_material_expressions(uv2, "", grass_c2, "UVs")
    uv3 = node(unreal.MaterialExpressionDivide, -1000, -850, const_b=12000.0)
    mel.connect_material_expressions(xy, "", uv3, "")
    macro = node(unreal.MaterialExpressionTextureSample, -700, -900, texture=tex("aerial_grass_rock_diff"))
    mel.connect_material_expressions(uv3, "", macro, "UVs")
    avg = node(unreal.MaterialExpressionAdd, -500, -500)
    mel.connect_material_expressions(grass_c, "RGB", avg, "A")
    mel.connect_material_expressions(grass_c2, "RGB", avg, "B")
    # The photo is dry, yellowish grass: halve (average) and tint toward fresh green.
    tint = node(unreal.MaterialExpressionMultiply, -380, -500)
    tint_c = node(unreal.MaterialExpressionConstant3Vector, -500, -380, constant=unreal.LinearColor(0.34, 0.5, 0.26, 0))
    mel.connect_material_expressions(avg, "", tint, "A")
    mel.connect_material_expressions(tint_c, "", tint, "B")
    macro_k = node(unreal.MaterialExpressionMultiply, -500, -800, const_b=1.1)
    mel.connect_material_expressions(macro, "R", macro_k, "")
    macro_b = node(unreal.MaterialExpressionAdd, -380, -800, const_b=0.55)
    mel.connect_material_expressions(macro_k, "", macro_b, "")
    grass_final = node(unreal.MaterialExpressionMultiply, -260, -500)
    mel.connect_material_expressions(tint, "", grass_final, "A")
    mel.connect_material_expressions(macro_b, "", grass_final, "B")

    color = node(unreal.MaterialExpressionLinearInterpolate, -200, -100)
    mel.connect_material_expressions(rock, "XYZ Texture", color, "A")
    mel.connect_material_expressions(grass_final, "", color, "B")
    mel.connect_material_expressions(flat, "", color, "Alpha")
    mel.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)

    rough = node(unreal.MaterialExpressionLinearInterpolate, -200, 150, const_a=0.9)
    mel.connect_material_expressions(grass_r, "R", rough, "B")
    mel.connect_material_expressions(flat, "", rough, "Alpha")
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)

    # Grass normal detail on flat ground only (cliffs keep the geometric normal).
    flat_n = node(unreal.MaterialExpressionConstant3Vector, -500, 300, constant=unreal.LinearColor(0, 0, 1, 0))
    nrm = node(unreal.MaterialExpressionLinearInterpolate, -200, 350)
    mel.connect_material_expressions(flat_n, "", nrm, "A")
    mel.connect_material_expressions(grass_n, "RGB", nrm, "B")
    mel.connect_material_expressions(flat, "", nrm, "Alpha")
    mel.connect_material_property(nrm, "", unreal.MaterialProperty.MP_NORMAL)

    mel.recompile_material(mat)
    lib.save_loaded_asset(mat, only_if_is_dirty=False)
    return mat


def rock_collision():
    for path in lib.list_assets(Q, recursive=True, include_folder=False):
        if "/StaticMeshes/" in path and "grass" not in path:
            m = unreal.load_asset(path)
            m.get_editor_property("body_setup").set_editor_property(
                "collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            lib.save_loaded_asset(m, only_if_is_dirty=False)


# ---- Placement helpers --------------------------------------------------------------------------
def ground(x_m, y_m):
    """(z_cm, normal) of the landscape under (x, y) metres."""
    world = lk.editor.get_editor_world()
    start = unreal.Vector(x_m * 100, y_m * 100, 50000)
    end = unreal.Vector(x_m * 100, y_m * 100, -50000)
    hit = unreal.SystemLibrary.line_trace_single(world, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                 False, [], unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        return 0.0, unreal.Vector(0, 0, 1)
    # HitResult's fields aren't exposed by name; its vectors come in a fixed order:
    # Location, ImpactPoint, Normal, ImpactNormal, TraceStart, TraceEnd.
    vectors = [v for v in hit.to_tuple() if isinstance(v, unreal.Vector)]
    return vectors[1].z, vectors[3]


def pit_d(x, y):
    return math.sqrt(((x - PIT_X) / RIM_RX) ** 2 + ((y - PIT_Y) / RIM_RY) ** 2)


def place_mesh(path, x, y, scale, label, sink=0.15):
    """A boulder as its own actor, sunk a little into the ground so it doesn't float."""
    z, _ = ground(x, y)
    mesh = unreal.load_asset(path)
    a = lk.actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x * 100, y * 100, z),
                                         unreal.Rotator(random.uniform(-6, 6), random.uniform(-6, 6), random.uniform(0, 360)))
    a.static_mesh_component.set_static_mesh(mesh)
    s = scale * random.uniform(0.85, 1.15)
    a.set_actor_scale3d(unreal.Vector(s, s, s * random.uniform(0.8, 1.1)))
    b = mesh.get_bounding_box()
    a.add_actor_world_offset(unreal.Vector(0, 0, -b.min.z * s - (b.max.z - b.min.z) * s * sink), False, False)
    a.set_actor_label(label)
    a.set_folder_path("Rocks")
    return a


def place_tree(path, x, y, label, folder):
    z, _ = ground(x, y)
    a = lk.actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(x * 100, y * 100, z - 20),
                                         unreal.Rotator(0, 0, random.uniform(0, 360)))
    a.skeletal_mesh_component.set_skinned_asset_and_update(unreal.load_asset(path))
    s = random.uniform(1.0, 1.4)
    a.set_actor_scale3d(unreal.Vector(s, s, s))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    return a


def place_static_tree(path, x, y, label, folder, scale=(0.8, 1.2)):
    z, _ = ground(x, y)
    a = lk.actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x * 100, y * 100, z - 30),
                                         unreal.Rotator(0, 0, random.uniform(0, 360)))
    a.static_mesh_component.set_static_mesh(unreal.load_asset(path))
    sc = random.uniform(*scale)
    a.set_actor_scale3d(unreal.Vector(sc, sc, sc))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    return a


P = Q + "Plants/"
FIRS = [P + "fir_tree_01/fir_tree_01_%s_LOD0" % v for v in "abc"]


def plant_meshes(name, keep=lambda p: True):
    return sorted(p.split(".")[0] for p in lib.list_assets(P + name, recursive=True, include_folder=False)
                  if unreal.EditorAssetLibrary.find_asset_data(p).asset_class_path.asset_name == "StaticMesh" and keep(p))


# ---- Build ------------------------------------------------------------------------------------
mask_parent = fix_grass_material()
terrain = terrain_material()
rock_collision()

lk.new_level(LEVEL)
lk.sky_and_light(sun_pitch=-48.0, sun_yaw=20.0)
lk.spawn(unreal.VolumetricCloud, 0, 0, 0, label="Clouds")

landscape = unreal.WorldBuilderLibrary.create_landscape_from_r16(
    lk.editor.get_editor_world(), HEIGHTMAP, 505, unreal.Vector(0, 0, 0), unreal.Vector(100, 100, 100), terrain, "Terrain")

# Boulders: a row along the far (east) rim like the reference skyline, plus scattered ones.
ROCKS = [Q + "boulder_01/boulder_01_1k/StaticMeshes/boulder_01_1k",
         Q + "namaqualand_boulder_02/namaqualand_boulder_02_1k/StaticMeshes/namaqualand_boulder_02_1k"] + \
        [Q + "rock_moss_set_01/rock_moss_set_01_1k/StaticMeshes/rock_moss_set_01_rock%02d" % i for i in range(1, 7)]
n = 0
for i in range(14):  # far rim, just outside the pit edge
    ang = math.radians(-60 + i * 9 + random.uniform(-3, 3))
    r = 1.08 + random.uniform(0, 0.08)
    place_mesh(random.choice(ROCKS), PIT_X + RIM_RX * r * math.cos(ang), PIT_Y + RIM_RY * r * math.sin(ang),
               random.uniform(1.6, 3.2), "Boulder_Rim_%02d" % i); n += 1
while n < 34:  # plateau, away from the pit
    x, y = random.uniform(-180, 200), random.uniform(-180, 180)
    if pit_d(x, y) > 1.25:
        place_mesh(random.choice(ROCKS), x, y, random.uniform(0.8, 2.4), "Boulder_%02d" % n); n += 1
for i in range(10):  # rubble on the quarry floor
    ang, r = random.uniform(0, 2 * math.pi), random.uniform(0.1, 0.6)
    place_mesh(random.choice(ROCKS), PIT_X + RIM_RX * r * math.cos(ang), PIT_Y + RIM_RY * r * math.sin(ang),
               random.uniform(0.7, 1.6), "Boulder_Floor_%02d" % i)

# Trees: broadleaf (aspen, hazel) along the far rim and in groves; each tree is its own actor.
ASPEN = [PVE + "Tree_European_QuakingAspen_01/SK_European_QuakingAspen_%02d" % i for i in (1, 2, 3)]
HAZEL = [PVE + "Tree_Common_Hazel_01/SK_CommonHazel_%02d" % i for i in (1, 2)]
t = 0
for i in range(46):  # far rim line behind the boulders, two rows deep
    ang = math.radians(-75 + i * 3.3 + random.uniform(-1.5, 1.5))
    r = 1.15 + random.uniform(0, 0.4)
    x, y = PIT_X + RIM_RX * r * math.cos(ang), PIT_Y + RIM_RY * r * math.sin(ang)
    if r > 1.35 and random.random() < 0.6:  # the back row is mostly pines, like the reference
        place_static_tree(random.choice(FIRS), x, y, "Fir_Rim_%02d" % i, "Trees/Rim")
    else:
        place_tree(random.choice(ASPEN + HAZEL), x, y, "Tree_Rim_%02d" % i, "Trees/Rim")
    t += 1
for g, (gx, gy) in enumerate([(-90, -110), (-120, 60), (20, 140), (180, 120), (200, -120), (-30, -170)]):
    for k in range(random.randint(20, 30)):  # groves on the plateau and far hills
        x, y = gx + random.gauss(0, 16), gy + random.gauss(0, 16)
        if pit_d(x, y) > 1.2:
            far = math.hypot(x - PIT_X, y - PIT_Y) > 150  # far groves: conifer forest; near: broadleaf
            if far and random.random() < 0.75:
                place_static_tree(random.choice(FIRS), x, y, "Fir_Grove%d_%02d" % (g, k), "Trees/Groves")
            else:
                place_tree(random.choice(ASPEN + ASPEN + HAZEL), x, y, "Tree_Grove%d_%02d" % (g, k), "Trees/Groves")
            t += 1

# Meadow: Foliage instances (Foliage tool can paint/erase them), densest around the viewpoint.
world = lk.editor.get_editor_world()
cam_x, cam_y = PIT_X - RIM_RX * 1.15, PIT_Y + 4   # viewpoint (metres)
NEAR = (unreal.Vector2D((cam_x - 30) * 100, (cam_y - 40) * 100), unreal.Vector2D((cam_x + 50) * 100, (cam_y + 40) * 100))
FAR = (unreal.Vector2D(-11000, -9000), unreal.Vector2D(5000, 9000))
MEADOW = [  # (meshes, near count each, far count each, scale range, cull cm)
    (plant_meshes("grass_medium_02"), 4500, 3000, (1.6, 2.6), 6000),
    (sorted(p.split(".")[0] for p in lib.list_assets(Q + "grass_medium_01", recursive=True, include_folder=False)
            if "/StaticMeshes/" in p and "_large_" in p), 700, 600, (1.4, 2.2), 6000),
    (plant_meshes("weed_plant_02"), 700, 300, (1.5, 2.5), 4000),
    (plant_meshes("celandine_01"), 350, 150, (1.2, 2.0), 4000),
    (plant_meshes("dandelion_01"), 250, 100, (1.2, 1.8), 4000),
    (plant_meshes("shrub_03"), 200, 150, (1.5, 2.5), 5000),
    (plant_meshes("fern_02"), 40, 120, (1.0, 1.6), 6000),
    (plant_meshes("pine_sapling_small") + plant_meshes("fir_sapling"), 15, 160, (1.0, 2.2), 15000),
]
placed = 0
for j, (meshes, near_n, far_n, (lo, hi), cull) in enumerate(MEADOW):
    for i, g in enumerate(meshes):
        mesh = unreal.load_asset(g)
        unreal.WorldBuilderLibrary.clear_foliage(world, mesh)
        placed += unreal.WorldBuilderLibrary.scatter_foliage(world, mesh, NEAR[0], NEAR[1], near_n, 1000 * j + i, lo, hi, 32.0, True, cull, False)
        placed += unreal.WorldBuilderLibrary.scatter_foliage(world, mesh, FAR[0], FAR[1], far_n, 1000 * j + 500 + i, lo, hi, 32.0, True, cull, False)

# Foreground grove: big trees just north of the viewpoint, framing the left of the shot.
for k in range(14):
    x, y = cam_x + random.uniform(-15, 35), cam_y - random.uniform(16, 55)
    if pit_d(x, y) > 1.02:
        place_tree(random.choice(ASPEN[:2] + HAZEL[:1]), x, y, "Tree_Foreground_%02d" % k, "Trees/Foreground"); t += 1

# The reference viewpoint: standing on the west rim, looking east across the pit at the far wall.
cz, _ = ground(cam_x, cam_y)
cam = lk.actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(cam_x * 100, cam_y * 100, cz + 350),
                                       unreal.Rotator(0, -4, 0))
cam.set_actor_label("ReferenceView")
cam.camera_component.set_editor_property("field_of_view", 60.0)

# Playable: our game mode (platforming character + HUD), a start at the viewpoint, and a
# render-to-texture camera that playtests move along with the player's camera to record video.
lk.use_platforming_game_mode()
lk.spawn(unreal.PlayerStart, cam_x * 100, cam_y * 100, cz + 120, label="PlayerStart")
lk.spawn(unreal.SceneCapture2D, cam_x * 100, cam_y * 100, cz + 400, label="WalkCam")

print("QUARRY BUILT landscape=%s rocks=%d trees=%d grass=%d mask_parent=%s actors=%d" % (
    landscape.get_actor_label() if landscape else None, n + 10, t, placed, mask_parent, lk.save()))
