"""Tree Lab beauty shots: walk through the forest at eye level, then pan along the lineup.

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
OUT = os.path.join(project, "Saved", "TreeLab_video")
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))


def world():
    return ues.get_editor_world()


def find(label):
    return next((a for a in actors.get_all_level_actors() if a.get_actor_label() == label), None)


levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if world().get_name() != "Lvl_TreeLab":
    levels.load_level("/Game/Maps/Lvl_TreeLab")
FIELD_CENTER = unreal.Vector(4000, 40000, 0)
ASPEN = "/ProceduralVegetationEditor/SampleAssets/Tree_European_QuakingAspen_01/SK_European_QuakingAspen_01"
# The experiment's forest, camera and lighting aren't saved in the level; recreate them.
if find("StressField") is None:
    f = actors.spawn_actor_from_class(unreal.TreeField, FIELD_CENTER)
    f.set_actor_label("StressField")
    f.set_editor_property("tree", unreal.load_asset(ASPEN))
    f.set_editor_property("spacing", 900.0)
if find("LabCam") is None:
    actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 500)).set_actor_label("LabCam")
ground = find("Ground")
ground.set_actor_location(FIELD_CENTER, False, False)
ground.set_actor_scale3d(unreal.Vector(10000, 10000, 1))
find("Sun").set_actor_rotation(unreal.Rotator(0.0, -40.0, 35.0), False)

for c in ("scalability 3", "r.DynamicGlobalIlluminationMethod 1", "r.ReflectionMethod 1", "r.Shadow.Virtual.Enable 1"):
    unreal.SystemLibrary.execute_console_command(world(), c)

field = find("StressField")
field.set_editor_property("rows", 200)
field.set_editor_property("columns", 200)
field.rebuild()
fc = field.get_actor_location()
half = 200 * 900.0 * 0.5

cam = find("LabCam")
rt = unreal.RenderingLibrary.create_render_target2d(world(), 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8)
comp = cam.capture_component2d
comp.set_editor_property("texture_target", rt)
comp.set_editor_property("fov_angle", 70.0)
comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
comp.set_editor_property("capture_every_frame", False)


def walk(t):
    # Enter the forest from its edge at eye height, drifting slightly side to side.
    x = fc.x - half + 200 + 260 * t
    y = fc.y + 300 * math.sin(t * 0.4)
    return unreal.Vector(x, y, 170), unreal.Rotator(0, 2, 8 * math.cos(t * 0.4))


def lineup(t):
    # Slow dolly along the lineup (cartoon tree -> Aspen 1), looking at it from the side.
    # The enlarged 10 km ground (centred on the forest) still covers the lineup.
    x = -300 + 900 * t
    return unreal.Vector(x, -1900, 450), unreal.Rotator(0, 2, 72)


SHOTS = [(walk, 10.0), (lineup, 9.0)]
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
