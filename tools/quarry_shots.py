"""Render still images of Lvl_Quarry through a SceneCapture2D (independent of the editor viewport).

Views: the ReferenceView camera (matches the reference frame) plus an overview and a ground-level
shot. Top quality (Epic + Lumen + virtual shadows); each view renders for a while first so Lumen
settles. Output: Saved/Quarry/<view>.png
"""
import os

import unreal

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), "Saved", "Quarry")
os.makedirs(OUT, exist_ok=True)
WARM_FRAMES = 60


def world():
    return ues.get_editor_world()


def find(label):
    return next((a for a in actors.get_all_level_actors() if a.get_actor_label() == label), None)


if world().get_name() != "Lvl_Quarry":
    levels.load_level("/Game/Maps/Lvl_Quarry")
for c in ("scalability 3", "r.DynamicGlobalIlluminationMethod 1", "r.ReflectionMethod 1", "r.Shadow.Virtual.Enable 1"):
    unreal.SystemLibrary.execute_console_command(world(), c)

ref = find("ReferenceView")
ref_loc, ref_rot = ref.get_actor_location(), ref.get_actor_rotation()
VIEWS = [
    ("reference_view", ref_loc, ref_rot, 60.0),
    ("overview", unreal.Vector(-6000, -14000, 9000), unreal.Rotator(0, -28, 50), 70.0),
    ("ground_level", ref_loc + unreal.Vector(1200, -1800, -200), unreal.Rotator(0, 2, 30), 70.0),
]

cam = find("ShotCam") or actors.spawn_actor_from_class(unreal.SceneCapture2D, ref_loc)
cam.set_actor_label("ShotCam")
rt = unreal.RenderingLibrary.create_render_target2d(world(), 1600, 900, unreal.TextureRenderTargetFormat.RTF_RGBA8)
comp = cam.capture_component2d
comp.set_editor_property("texture_target", rt)
comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
comp.set_editor_property("capture_every_frame", False)

st = {"view": 0, "frame": 0, "handle": None}


def tick(_dt):
    try:
        if st["view"] >= len(VIEWS):
            unreal.unregister_slate_post_tick_callback(st["handle"])
            for c in ("scalability 1", "r.DynamicGlobalIlluminationMethod 0", "r.ReflectionMethod 2", "r.Shadow.Virtual.Enable 0"):
                unreal.SystemLibrary.execute_console_command(world(), c)
            unreal.log("QUARRY SHOTS DONE %d" % len(VIEWS))
            return
        name, loc, rot, fov = VIEWS[st["view"]]
        if st["frame"] == 0:
            cam.set_actor_location_and_rotation(loc, rot, False, False)
            comp.set_editor_property("fov_angle", fov)
        comp.capture_scene()
        st["frame"] += 1
        if st["frame"] >= WARM_FRAMES:
            unreal.RenderingLibrary.export_render_target(world(), rt, OUT, name + ".png")
            unreal.log("QUARRY SHOT %s" % name)
            st.update(view=st["view"] + 1, frame=0)
    except Exception as exc:
        unreal.unregister_slate_post_tick_callback(st["handle"])
        unreal.log_error("quarry shots error: %r" % exc)


st["handle"] = unreal.register_slate_post_tick_callback(tick)
unreal.log("QUARRY SHOTS STARTED")
