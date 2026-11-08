"""Quarry walkthrough (from treelab_flythrough.py): pan from the reference view, then a rim walk.\n\nTree Lab beauty shots: walk through the forest at eye level, then pan along the lineup.

Best quality (Epic + Lumen + virtual shadows). The camera moves a fixed step per captured frame,
so the video plays at a steady 24 fps no matter how slow capturing is. Frames go to Saved/TreeLab_video.
"""
import math
import os

import unreal

FPS = 24
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
project = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
OUT = os.path.join(project, "Saved", "Quarry_video")
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))


def world():
    return ues.get_editor_world()


def find(label):
    return next((a for a in actors.get_all_level_actors() if a.get_actor_label() == label), None)


levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if world().get_name() != "Lvl_Quarry":
    levels.load_level("/Game/Maps/Lvl_Quarry")
for c in ("scalability 3", "r.DynamicGlobalIlluminationMethod 1", "r.ReflectionMethod 1", "r.Shadow.Virtual.Enable 1"):
    unreal.SystemLibrary.execute_console_command(world(), c)

ref = find("ReferenceView")
r0, rr = ref.get_actor_location(), ref.get_actor_rotation()
cam = find("VideoCam") or actors.spawn_actor_from_class(unreal.SceneCapture2D, r0)
cam.set_actor_label("VideoCam")
rt = unreal.RenderingLibrary.create_render_target2d(world(), 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8)
comp = cam.capture_component2d
comp.set_editor_property("texture_target", rt)
comp.set_editor_property("fov_angle", 65.0)
comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
comp.set_editor_property("capture_every_frame", False)


def pan(t):
    # From the reference viewpoint, a slow pan left-to-right across the quarry.
    return r0, unreal.Rotator(0, rr.pitch, -25 + 9 * t)


def rim_walk(t):
    # Walk south along the west rim at eye height, looking out over the pit.
    x, y = r0.x + 150 * t, r0.y + 300 + 260 * t
    return unreal.Vector(x, y, r0.z - 150), unreal.Rotator(0, -3, -20 + 3 * t)


SHOTS = [(pan, 7.0), (rim_walk, 8.0)]
WARMUP = 45  # frames for Lumen and shadows to settle at the start of each shot
st = {"shot": 0, "frame": 0, "warm": WARMUP, "n": 0, "handle": None}


def tick(_dt):
    try:
        if st["shot"] >= len(SHOTS):
            unreal.unregister_slate_post_tick_callback(st["handle"])
            for c in ("scalability 1", "r.DynamicGlobalIlluminationMethod 0", "r.ReflectionMethod 2", "r.Shadow.Virtual.Enable 0"):
                unreal.SystemLibrary.execute_console_command(world(), c)
            unreal.log("FLYTHROUGH DONE frames=%d" % st["n"])
            return
        path, seconds = SHOTS[st["shot"]]
        t = st["frame"] / FPS
        loc, rot = path(t)
        cam.set_actor_location_and_rotation(loc, rot, False, False)
        comp.capture_scene()
        if st["warm"] > 0:
            st["warm"] -= 1
            return
        unreal.RenderingLibrary.export_render_target(world(), rt, OUT, "f_%05d.png" % st["n"])
        st["n"] += 1
        st["frame"] += 1
        if st["frame"] >= seconds * FPS:
            st.update(shot=st["shot"] + 1, frame=0, warm=WARMUP)
    except Exception as exc:
        unreal.unregister_slate_post_tick_callback(st["handle"])
        unreal.log_error("flythrough error: %r" % exc)


st["handle"] = unreal.register_slate_post_tick_callback(tick)
unreal.log("FLYTHROUGH STARTED")
