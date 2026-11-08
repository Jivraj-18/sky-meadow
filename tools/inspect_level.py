import unreal
from collections import Counter

actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
print("actors:", len(actors))
print(Counter(a.get_class().get_name() for a in actors).most_common(15))

for a in actors:
    cls = a.get_class().get_name()
    if cls in ("PlayerStart",) or "BP_" in cls:
        print(cls, a.get_actor_label(), a.get_actor_location())

# Overall bounds of the course
xs, ys, zs = [], [], []
for a in actors:
    if a.get_class().get_name() == "StaticMeshActor":
        l = a.get_actor_location()
        xs.append(l.x); ys.append(l.y); zs.append(l.z)
if xs:
    print("bounds x", min(xs), max(xs), "y", min(ys), max(ys), "z", min(zs), max(zs))

bp = unreal.load_asset("/Game/Variant_Platforming/Blueprints/BP_PlatformingCharacter")
cdo = unreal.get_default_object(bp.generated_class())
for prop in ("jump_max_count", "jump_max_hold_time"):
    print(prop, cdo.get_editor_property(prop))
mv = cdo.get_editor_property("character_movement")
for prop in ("max_walk_speed", "jump_z_velocity", "air_control", "gravity_scale"):
    print(prop, mv.get_editor_property(prop))
print("BP functions:", [f for f in dir(cdo) if "dash" in f.lower() or "wall" in f.lower() or "jump" in f.lower()][:30])
