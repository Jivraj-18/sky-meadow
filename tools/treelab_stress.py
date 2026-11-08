"""Tree Lab experiment, run inside the live editor (tools/ue.py tools/treelab_stress.py).

Phases: 1) photo of each tree in the lineup, 2) forest stress test (Aspen 1, growing tree count),
3) quality ladder at a fixed forest size. Every stage settles, measures frame times from the
editor's own tick and VRAM from nvidia-smi, then takes a viewport screenshot. Results are written
after every stage to Saved/TreeLab/results.json, so a GPU crash still leaves the data up to it.
"""
import json
import math
import os
import subprocess
import time

import unreal

PVE = "/ProceduralVegetationEditor/SampleAssets/"
ASPEN = PVE + "Tree_European_QuakingAspen_01/SK_European_QuakingAspen_01"
SETTLE, MEASURE = 3.0, 4.0
BREAK_FPS = 3.0
STRESS_COUNTS = globals().get("TREELAB_COUNTS", [1, 16, 100, 400, 1024, 2500, 5041, 10000, 20164, 40000])
PHASES = globals().get("TREELAB_PHASES", ["showcase", "stress", "quality"])
SPACING = 900.0
FIELD_CENTER = unreal.Vector(4000, 40000, 0)  # well away from the lineup

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
project = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
OUT = os.path.join(project, "Saved", "TreeLab")
SHOTS = os.path.join(project, "Saved", "Screenshots", "LinuxEditor")
os.makedirs(OUT, exist_ok=True)
for d in (OUT, SHOTS):
    for f in os.listdir(d) if os.path.isdir(d) else []:
        if f.endswith((".png", ".json")):
            os.remove(os.path.join(d, f))


def world():
    return ues.get_editor_world()


CAM = {}


def lab_camera():
    """Render-to-texture camera: rendered explicitly each tick, so measurements and screenshots
    don't depend on the editor viewport being drawn (it isn't while the window is covered)."""
    if "actor" not in CAM:
        cam = find("LabCam") or actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 500))
        cam.set_actor_label("LabCam")
        rt = unreal.RenderingLibrary.create_render_target2d(world(), 1280, 720,
                                                            unreal.TextureRenderTargetFormat.RTF_RGBA8)
        comp = cam.capture_component2d
        comp.set_editor_property("texture_target", rt)
        comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        comp.set_editor_property("capture_every_frame", False)
        comp.set_editor_property("fov_angle", 75.0)
        CAM.update(actor=cam, comp=comp, rt=rt)
    return CAM


def set_cam(loc, rot):
    c = lab_camera()
    c["actor"].set_actor_location_and_rotation(loc, rot, False, False)


def render():
    lab_camera()["comp"].capture_scene()


def console(cmd):
    unreal.SystemLibrary.execute_console_command(world(), cmd)


def vram():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                              "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5).stdout
        used, total, util = [int(x) for x in out.strip().split(",")]
        return {"vram_mb": used, "vram_total_mb": total, "gpu_util": util}
    except Exception as exc:  # nvidia-smi missing or busy
        return {"vram_error": repr(exc)}


def find(label):
    for a in actors.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


def field():
    f = find("StressField")
    if f is None:
        f = actors.spawn_actor_from_class(unreal.TreeField, FIELD_CENTER)
        f.set_actor_label("StressField")
        f.set_editor_property("tree", unreal.load_asset(ASPEN))
        f.set_editor_property("spacing", SPACING)
    return f


def set_forest(count):
    side = int(round(math.sqrt(count)))
    f = field()
    f.set_editor_property("rows", side)
    f.set_editor_property("columns", side)
    f.rebuild()
    return side * side


def forest_camera(side):
    # Stand just outside the forest's near edge, high up, looking in across the canopy.
    half = side * SPACING * 0.5
    big = side > 200  # huge forests: climb higher and look down across more of it
    eye = unreal.Vector(FIELD_CENTER.x - half - 2500, FIELD_CENTER.y, 12000 if big else 3000)
    set_cam(eye, unreal.Rotator(0, -30 if big else -18, 0))


# ---- Stage list ---------------------------------------------------------------------------
STAGES = []
LINEUP = [("Cartoon kit tree", 0, 430), ("Hazel 4 (0.9 m)", 600, 90), ("Hazel 3 (1.7 m)", 1100, 170),
          ("Hazel 2 (2.9 m)", 1700, 290), ("Hazel 1 (4.7 m)", 2500, 470), ("Aspen 4 (4.5 m)", 3500, 450),
          ("Aspen 3 (7.1 m)", 4600, 710), ("Aspen 2 (10.4 m)", 6000, 1040), ("Aspen 1 (14 m)", 7800, 1400)]
for label, x, h in LINEUP:
    def setup(x=x, h=h):
        dist = max(350.0, h * 1.6)
        set_cam(unreal.Vector(x - dist * 0.7, -dist * 0.7, h * 0.55),
                                           unreal.Rotator(0, -5, 45))
    STAGES.append({"phase": "showcase", "name": label, "setup": setup})
STAGES.append({"phase": "showcase", "name": "Lineup overview", "setup": lambda: set_cam(
    unreal.Vector(3900, -5200, 900), unreal.Rotator(0, -8, 90))})

for n in STRESS_COUNTS:
    def setup(n=n):
        side = int(round(math.sqrt(n)))
        set_forest(n)
        forest_camera(side)
    STAGES.append({"phase": "stress", "name": "%d trees" % n, "count": n, "setup": setup})

QUALITY = [("Low", ["scalability 0"]), ("Medium", ["scalability 1"]), ("High", ["scalability 2"]),
           ("Epic", ["scalability 3"]),
           ("Epic + Lumen + virtual shadows", ["scalability 3", "r.DynamicGlobalIlluminationMethod 1",
                                               "r.ReflectionMethod 1", "r.Shadow.Virtual.Enable 1"])]
QUALITY_TREES = globals().get("TREELAB_QUALITY_TREES", 1024)
for name, cmds in QUALITY:
    def setup(cmds=cmds):
        side = int(round(math.sqrt(QUALITY_TREES)))
        set_forest(side * side)
        forest_camera(side)
        for c in cmds:
            console(c)
    STAGES.append({"phase": "quality", "name": "%s (%d trees)" % (name, QUALITY_TREES), "setup": setup})


STAGES = [s for s in STAGES if s["phase"] in PHASES]


# ---- Runner (one stage at a time, driven by the editor tick) ----------------------------------
st = {"i": 0, "phase": "setup", "t": 0.0, "dts": [], "results": [], "broken": False, "handle": None}


def save_results():
    json.dump(st["results"], open(os.path.join(OUT, "results.json"), "w"), indent=1)


def finish(reason):
    unreal.unregister_slate_post_tick_callback(st["handle"])
    for c in ("scalability 1", "r.DynamicGlobalIlluminationMethod 0", "r.ReflectionMethod 2", "r.Shadow.Virtual.Enable 0"):
        console(c)  # back to the project's safe defaults
    save_results()
    unreal.log("TREELAB DONE %s stages=%d" % (reason, len(st["results"])))


def collect_shot(stage_index):
    name = "%02d.png" % stage_index  # export_render_target writes PNG under exactly this name
    unreal.RenderingLibrary.export_render_target(world(), lab_camera()["rt"], OUT, name)
    return name if os.path.exists(os.path.join(OUT, name)) else None


def tick(dt):
    try:
        if st["i"] >= len(STAGES):
            finish("all stages")
            return
        stage = STAGES[st["i"]]
        if stage["phase"] == "stress" and st["broken"]:
            st["i"] += 1
            return
        st["t"] += dt
        if st["phase"] != "setup":
            render()
        if st["phase"] == "setup":
            stage["setup"]()
            st.update(phase="settle", t=0.0, dts=[])
            unreal.log("TREELAB STAGE %s: %s" % (stage["phase"], stage["name"]))
        elif st["phase"] == "settle" and st["t"] >= SETTLE:
            st.update(phase="measure", t=0.0, dts=[])
        elif st["phase"] == "measure":
            st["dts"].append(dt)
            if st["t"] >= MEASURE:
                dts = sorted(st["dts"])
                avg = len(dts) / sum(dts)
                low = 1.0 / dts[max(0, int(len(dts) * 0.99) - 1)]  # 1% low
                rec = {"phase": stage["phase"], "name": stage["name"], "fps": round(avg, 1),
                       "fps_1pct_low": round(low, 1), "frame_ms_max": round(dts[-1] * 1000, 1),
                       "frames": len(dts), **vram()}
                if "count" in stage:
                    rec["trees"] = stage["count"]
                st["results"].append(rec)
                save_results()
                unreal.log("TREELAB RESULT %s" % json.dumps(rec))
                if stage["phase"] == "stress" and avg < BREAK_FPS:
                    st["broken"] = True
                st.update(phase="shot", t=0.0)
        elif st["phase"] == "shot" and st["t"] >= 0.2:
            st["results"][-1]["image"] = collect_shot(st["i"])
            save_results()
            st.update(i=st["i"] + 1, phase="setup", t=0.0)
    except Exception as exc:
        unreal.log_error("treelab error: %r" % exc)
        finish("error %r" % exc)


if ues.get_editor_world().get_name() != "Lvl_TreeLab":
    levels.load_level("/Game/Maps/Lvl_TreeLab")
levels.editor_set_game_view(True)
console("scalability 1")
# Ground under the stress forest too (up to 1000x1000 trees x 9 m = 9 km).
ground = find("Ground")
if ground and "stress" in PHASES:
    ground.set_actor_location(unreal.Vector(FIELD_CENTER.x, FIELD_CENTER.y, 0), False, False)
    ground.set_actor_scale3d(unreal.Vector(10000, 10000, 1))
# Light the trees from behind the cameras (they mostly look north-east), not backlit.
sun = find("Sun")
if sun:
    sun.set_actor_rotation(unreal.Rotator(0.0, -40.0, 35.0), False)  # roll, pitch, yaw
st["handle"] = unreal.register_slate_post_tick_callback(tick)
unreal.log("TREELAB STARTED %d stages" % len(STAGES))
