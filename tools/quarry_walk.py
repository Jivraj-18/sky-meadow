"""Walk the player character around Lvl_Quarry in PIE and record it.

The bot steers along rim waypoints (staying outside the pit), jumps now and then and turns the
camera toward where it's going. Each frame the level's "WalkCam" SceneCapture2D is moved onto the
player's camera and rendered to Saved/Quarry_walk (works even if the editor window isn't drawn).
"""
import math
import os
import time

import unreal

PIT_X, PIT_Y = 5500.0, 1000.0
# Waypoints (cm): from the viewpoint south along the west rim, then east along the south rim.
WAYPOINTS = [(-3100, 1400), (-2900, 4200), (-1200, 7200), (1800, 8600), (5000, 8800), (8200, 8200), (10500, 6500)]
DURATION = 28.0   # game seconds
SLOMO = 0.0625    # game runs 16x slower while recording: export is ~0.6 s/frame -> ~24 frames per game second

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
project = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
OUT = os.path.join(project, "Saved", "Quarry_walk")
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))

if ues.get_editor_world().get_name() != "Lvl_Quarry":
    levels.load_level("/Game/Maps/Lvl_Quarry")
# Medium quality: ~22 fps in PIE on the 4 GB GPU (Epic + Lumen is ~8 fps with this much foliage).
QUALITY = ["scalability 1", "r.DynamicGlobalIlluminationMethod 0", "r.ReflectionMethod 2", "r.Shadow.Virtual.Enable 0"]
for c in QUALITY:
    unreal.SystemLibrary.execute_console_command(ues.get_editor_world(), c)

st = {"t0": None, "wp": 0, "n": 0, "yaw": None, "last_jump": 0.0, "handle": None, "rt": None, "cam": None, "done": False}


def finish(reason):
    if st["done"]:
        return
    st["done"] = True
    unreal.unregister_slate_post_tick_callback(st["handle"])
    levels.editor_request_end_play()
    for c in ("scalability 1", "r.DynamicGlobalIlluminationMethod 0", "r.ReflectionMethod 2", "r.Shadow.Virtual.Enable 0"):
        unreal.SystemLibrary.execute_console_command(ues.get_editor_world(), c)
    unreal.log("QUARRY WALK DONE %s frames=%d" % (reason, st["n"]))


def tick(dt):
    if st["done"]:
        return
    try:
        world = ues.get_game_world()
        pawn = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
        if pawn is None:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)  # game time (slowed by SLOMO)
        dt = dt * SLOMO
        if st["t0"] is None:
            unreal.SystemLibrary.execute_console_command(world, "slomo %f" % SLOMO)
            st["t0"] = now + 0.3
            cams = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SceneCapture2D)
                    if a.get_actor_label() == "WalkCam"]
            st["cam"] = cams[0]
            st["rt"] = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8)
            comp = st["cam"].capture_component2d
            comp.set_editor_property("texture_target", st["rt"])
            comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            comp.set_editor_property("capture_every_frame", False)
            comp.set_editor_property("fov_angle", 85.0)
        t = now - st["t0"]
        if t < 0:
            return
        if t > DURATION or st["wp"] >= len(WAYPOINTS):
            finish("route complete" if st["wp"] >= len(WAYPOINTS) else "time")
            return

        # Steer toward the current waypoint.
        loc = pawn.get_actor_location()
        tx, ty = WAYPOINTS[st["wp"]]
        dx, dy = tx - loc.x, ty - loc.y
        if math.hypot(dx, dy) < 250:
            st["wp"] += 1
            return
        d = math.hypot(dx, dy)
        pawn.add_movement_input(unreal.Vector(dx / d, dy / d, 0), 1.0)
        if now - st["last_jump"] > 4.5 and t > 3:
            pawn.jump()
            st["last_jump"] = now
        elif now - st["last_jump"] > 0.35:
            pawn.stop_jumping()

        # Camera: ease toward the walking direction, looking slightly down.
        want = math.degrees(math.atan2(dy, dx))
        st["yaw"] = want if st["yaw"] is None else st["yaw"] + ((want - st["yaw"] + 180) % 360 - 180) * min(1.0, dt * 2.0)
        pc = unreal.GameplayStatics.get_player_controller(world, 0)
        pc.set_control_rotation(unreal.Rotator(0, -12, st["yaw"]))

        # Record through the player's camera.
        cm = unreal.GameplayStatics.get_player_camera_manager(world, 0)
        st["cam"].set_actor_location_and_rotation(cm.get_camera_location(), cm.get_camera_rotation(), False, False)
        st["cam"].capture_component2d.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, st["rt"], OUT, "f_%05d.png" % st["n"])
        st["n"] += 1
    except Exception as exc:
        unreal.log_error("quarry walk error: %r" % exc)
        finish("error")


st["handle"] = unreal.register_slate_post_tick_callback(tick)
levels.editor_request_begin_play()
unreal.log("QUARRY WALK STARTED")
