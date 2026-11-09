"""Quarry: a dirt road loop around the pit (Landscape Spline, editable in Landscape mode > Splines)
and a drivable off-road car the soldier can get into with E. Run in the live editor:
the Splines edit layer carves the terrain over the next editor frames; then save the level.
"""
import math
import os
import random

import unreal

lib = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SRC = os.path.expanduser("~/unreal-tests/assets_src/polyhaven/brown_mud_dry")
PIT_X, PIT_Y, RIM_RX, RIM_RY = 5500.0, 1000.0, 7500.0, 5500.0  # cm, as in build_quarry.py
ROAD_R = 1.75            # road loop radius as a multiple of the pit rim
HALF_WIDTH = 300.0       # 6 m wide dirt road
CAR = "/Game/VehicleTemplate/Blueprints/OffroadCar/BP_VehicleAdvOffroadCar"
random.seed(5)

if ues.get_editor_world().get_name() != "Lvl_Quarry":
    levels.load_level("/Game/Maps/Lvl_Quarry")
world = ues.get_editor_world()

# ---- Dirt road material (top-down world projection, so curves never stretch it) ---------------
manager = unreal.InterchangeManager.get_interchange_manager_scripted()
for f in sorted(os.listdir(SRC)):
    params = unreal.ImportAssetParameters()
    params.is_automated = True
    params.replace_existing = True
    manager.import_asset("/Game/Quarry/Road", unreal.InterchangeManager.create_source_data(os.path.join(SRC, f)), params)
    t = unreal.load_asset("/Game/Quarry/Road/" + os.path.splitext(f)[0])
    if "_nor_gl" in f:
        t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        t.set_editor_property("flip_green_channel", True)
        t.set_editor_property("srgb", False)
    elif "_rough" in f or "_arm" in f:
        t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        t.set_editor_property("srgb", False)
    lib.save_loaded_asset(t, only_if_is_dirty=False)

MAT = "/Game/Quarry/Road/M_DirtRoad"
if lib.does_asset_exist(MAT):
    mat = unreal.load_asset(MAT)
else:
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_DirtRoad", "/Game/Quarry/Road", unreal.Material, unreal.MaterialFactoryNew())
    wp = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -900, 0)
    xy = mel.create_material_expression(mat, unreal.MaterialExpressionComponentMask, -750, 0)
    xy.set_editor_property("r", True); xy.set_editor_property("g", True)
    xy.set_editor_property("b", False); xy.set_editor_property("a", False)
    mel.connect_material_expressions(wp, "", xy, "")
    uv = mel.create_material_expression(mat, unreal.MaterialExpressionDivide, -600, 0)
    uv.set_editor_property("const_b", 350.0)
    mel.connect_material_expressions(xy, "", uv, "")
    samples = {}
    for i, (name, kind) in enumerate((("brown_mud_dry_diff", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR),
                                      ("brown_mud_dry_nor_gl", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL),
                                      ("brown_mud_dry_rough", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS))):
        s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -350, -200 + 220 * i)
        s.set_editor_property("texture", unreal.load_asset("/Game/Quarry/Road/" + name))
        s.set_editor_property("sampler_type", kind)
        mel.connect_material_expressions(uv, "", s, "UVs")
        samples[name] = s
    mel.connect_material_property(samples["brown_mud_dry_diff"], "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(samples["brown_mud_dry_nor_gl"], "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.connect_material_property(samples["brown_mud_dry_rough"], "R", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    lib.save_loaded_asset(mat, only_if_is_dirty=False)

# ---- Road loop ----------------------------------------------------------------------------------
N = 18
points = []
for i in range(N):
    a = 2 * math.pi * i / N
    r = ROAD_R + random.uniform(-0.08, 0.08)
    points.append(unreal.Vector(PIT_X + RIM_RX * r * math.cos(a), PIT_Y + RIM_RY * r * math.sin(a), 0))

landscape = next(a for a in actors.get_all_level_actors() if isinstance(a, unreal.Landscape))
made = unreal.WorldBuilderLibrary.create_landscape_road(world, landscape, points, HALF_WIDTH, 600.0,
                                                        unreal.load_asset("/Engine/BasicShapes/Plane"), mat, True)


def dist_to_road(loc):
    best = 1e12
    for i in range(N):
        a, b = points[i], points[(i + 1) % N]
        abx, aby = b.x - a.x, b.y - a.y
        t = max(0.0, min(1.0, ((loc.x - a.x) * abx + (loc.y - a.y) * aby) / max(abx * abx + aby * aby, 1.0)))
        best = min(best, math.hypot(loc.x - (a.x + abx * t), loc.y - (a.y + aby * t)))
    return best


# Clear the way: trees/boulders on the road, and grass on the road.
removed = 0
for a in actors.get_all_level_actors():
    folder = str(a.get_folder_path())
    if (folder.startswith("Trees") or folder.startswith("Rocks")) and dist_to_road(a.get_actor_location()) < HALF_WIDTH + 400:
        actors.destroy_actor(a)
        removed += 1
grass = unreal.WorldBuilderLibrary.remove_foliage_along_path(world, points, HALF_WIDTH + 80, True)

# ---- Car parked on the road nearest the player's start ---------------------------------------
start = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == "PlayerStart").get_actor_location()
i = min(range(N), key=lambda k: math.hypot(points[k].x - start.x, points[k].y - start.y))
p, q = points[i], points[(i + 1) % N]
yaw = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(p.x, p.y, 50000), unreal.Vector(p.x, p.y, -50000),
                                             unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
z = [v for v in hit.to_tuple() if isinstance(v, unreal.Vector)][1].z if hit else 0.0
for a in actors.get_all_level_actors():
    if a.get_actor_label() == "OffroadCar":
        actors.destroy_actor(a)
car = actors.spawn_actor_from_class(unreal.load_asset(CAR).generated_class(), unreal.Vector(p.x, p.y, z + 120), unreal.Rotator(0, 0, yaw))
car.set_actor_label("OffroadCar")
car.set_folder_path("Vehicles")

# ---- Soldier can get in with E ----------------------------------------------------------------
bp = unreal.load_asset("/Game/Soldier/BP_SoldierCharacter")
subs = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib_sub = unreal.SubobjectDataBlueprintFunctionLibrary
handles = subs.k2_gather_subobject_data_for_blueprint(bp)
entry = next((lib_sub.get_object(lib_sub.get_data(h)) for h in handles
              if isinstance(lib_sub.get_object(lib_sub.get_data(h)), unreal.VehicleEntry)), None)
if entry is None:
    handle, _ = subs.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=unreal.VehicleEntry, blueprint_context=bp))
    entry = lib_sub.get_object(lib_sub.get_data(handle))
entry.set_editor_property("driving_mapping_contexts", [unreal.load_asset("/Game/VehicleTemplate/Input/IMC_Vehicle_Default"),
                                                       unreal.load_asset("/Game/VehicleTemplate/Input/IMC_Vehicle_MouseLook")])
entry.set_editor_property("on_foot_mapping_contexts", [unreal.load_asset("/Game/Input/IMC_Default")])
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
lib.save_loaded_asset(bp, only_if_is_dirty=False)

print("ROAD BUILT points=%d removed_actors=%d removed_grass=%d car=%s at %s yaw=%.0f" % (
    made, removed, grass, car.get_name(), car.get_actor_location(), yaw))
