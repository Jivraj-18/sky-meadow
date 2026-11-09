"""Record the soldier walking up to the off-road car, getting in (E), driving the dirt road around
the quarry, and getting out. Same capture approach as quarry_walk.py (slomo + SceneCapture "WalkCam").
"""
import math
import os
import random

import unreal

PIT_X, PIT_Y, RIM_RX, RIM_RY = 5500.0, 1000.0, 7500.0, 5500.0
N = 18
random.seed(5)  # same road points as build_quarry_road.py
ROAD = []
for i in range(N):
    a = 2 * math.pi * i / N
    r = 1.75 + random.uniform(-0.08, 0.08)
    ROAD.append((PIT_X + RIM_RX * r * math.cos(a), PIT_Y + RIM_RY * r * math.sin(a)))

WALK_TIME, DRIVE_TIME, DURATION = 6.0, 24.0, 33.0   # game seconds
SLOMO = 0.0625

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
project = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
OUT = os.path.join(project, "Saved", "Quarry_drive")
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))
if ues.get_editor_world().get_name() != "Lvl_Quarry":
    levels.load_level("/Game/Maps/Lvl_Quarry")
for c in ("scalability 1", "r.DynamicGlobalIlluminationMethod 0", "r.ReflectionMethod 2", "r.Shadow.Virtual.Enable 0"):
    unreal.SystemLibrary.execute_console_command(ues.get_editor_world(), c)

st = {"t0": None, "n": 0, "yaw": None, "pitch": -12.0, "handle": None, "rt": None, "cam": None, "done": False,
      "phase": "walk", "soldier": None, "car": None, "wp": None, "log": []}


def finish(reason):
    if st["done"]:
        return
    st["done"] = True
    unreal.unregister_slate_post_tick_callback(st["handle"])
    levels.editor_request_end_play()
    unreal.log("QUARRY DRIVE DONE %s frames=%d %s" % (reason, st["n"], " | ".join(st["log"])))


def ease_camera(pc, want_yaw, want_pitch, dt, rate):
    if st["yaw"] is None:
        st["yaw"] = want_yaw
    st["yaw"] += ((want_yaw - st["yaw"] + 180) % 360 - 180) * min(1.0, dt * rate)
    st["pitch"] += (want_pitch - st["pitch"]) * min(1.0, dt * rate)
    pc.set_control_rotation(unreal.Rotator(0, st["pitch"], st["yaw"]))


def tick(dt):
    if st["done"]:
        return
    try:
        world = ues.get_game_world()
        pawn = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
        if pawn is None:
            return
        now = unreal.GameplayStatics.get_time_seconds(world)
        dt = dt * SLOMO
        pc = unreal.GameplayStatics.get_player_controller(world, 0)
        if st["t0"] is None:
            unreal.SystemLibrary.execute_console_command(world, "slomo %f" % SLOMO)
            st["t0"] = now + 0.5
            st["soldier"] = pawn
            st["car"] = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.WheeledVehiclePawn)][0]
            c = st["car"].get_actor_location()
            # Start a short walk away from the parked car (behind-left of it).
            fwd = st["car"].get_actor_forward_vector()
            right = st["car"].get_actor_right_vector()
            start = unreal.Vector(c.x - fwd.x * 900 - right.x * 700, c.y - fwd.y * 900 - right.y * 700, c.z + 300)
            pawn.set_actor_location(start, False, True)
            st["cam"] = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SceneCapture2D)
                         if a.get_actor_label() == "WalkCam"][0]
            st["rt"] = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8)
            comp = st["cam"].capture_component2d
            comp.set_editor_property("texture_target", st["rt"])
            comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            comp.set_editor_property("capture_every_frame", False)
            comp.set_editor_property("fov_angle", 85.0)
            return
        t = now - st["t0"]
        if t < 0:
            return
        if t > DURATION:
            finish("time")
            return
        car = st["car"]
        soldier = st["soldier"]
        entry = soldier.get_component_by_class(unreal.VehicleEntry)
        move = car.get_component_by_class(unreal.ChaosVehicleMovementComponent)

        if st["phase"] == "walk":
            loc, c = soldier.get_actor_location(), car.get_actor_location()
            # aim for the driver's side door
            right = car.get_actor_right_vector()
            tx, ty = c.x - right.x * 250, c.y - right.y * 250
            dx, dy = tx - loc.x, ty - loc.y
            d = math.hypot(dx, dy)
            if d > 120:
                soldier.add_movement_input(unreal.Vector(dx / d, dy / d, 0), 1.0)
            ease_camera(pc, math.degrees(math.atan2(c.y - loc.y, c.x - loc.x)), -12, dt, 2.5)
            if d < 200 or t > WALK_TIME:
                ok = entry.enter_nearest_vehicle()
                st["log"].append("enter=%s at t=%.1f" % (ok, t))
                move.set_handbrake_input(False)
                # the road point just ahead of the car
                c = car.get_actor_location()
                i = min(range(N), key=lambda k: math.hypot(ROAD[k][0] - c.x, ROAD[k][1] - c.y))
                st["wp"] = (i + 1) % N
                st["phase"] = "drive"
                st["t_drive"] = t
        elif st["phase"] == "drive":
            c = car.get_actor_location()
            tx, ty = ROAD[st["wp"]]
            if math.hypot(tx - c.x, ty - c.y) < 1500:
                st["wp"] = (st["wp"] + 1) % N
                tx, ty = ROAD[st["wp"]]
            yaw = car.get_actor_rotation().yaw
            err = (math.degrees(math.atan2(ty - c.y, tx - c.x)) - yaw + 180) % 360 - 180
            speed = move.get_forward_speed()
            move.set_steering_input(max(-1.0, min(1.0, err / 25.0)))
            want = 1600.0 if abs(err) < 20 else 900.0   # cm/s
            move.set_throttle_input(0.8 if speed < want else 0.0)
            move.set_brake_input(0.4 if speed > want + 400 else 0.0)
            ease_camera(pc, yaw, -10, dt, 2.0)
            if t - st["t_drive"] > DRIVE_TIME:
                move.set_throttle_input(0.0)
                move.set_brake_input(1.0)
                st["phase"] = "stop"
                st["log"].append("max speed seen ok, braking at t=%.1f" % t)
        elif st["phase"] == "stop":
            move.set_brake_input(1.0)
            ease_camera(pc, car.get_actor_rotation().yaw, -10, dt, 2.0)
            if abs(move.get_forward_speed()) < 50:
                move.set_brake_input(0.0)
                entry.exit_vehicle()
                st["log"].append("exit at t=%.1f" % t)
                st["phase"] = "out"
        else:
            c = car.get_actor_location()
            loc = soldier.get_actor_location()
            ease_camera(pc, math.degrees(math.atan2(c.y - loc.y, c.x - loc.x)) + 25, -12, dt, 1.5)
            if t > DURATION - 0.1:
                finish("done")
                return

        cm = unreal.GameplayStatics.get_player_camera_manager(world, 0)
        st["cam"].set_actor_location_and_rotation(cm.get_camera_location(), cm.get_camera_rotation(), False, False)
        st["cam"].capture_component2d.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, st["rt"], OUT, "f_%05d.png" % st["n"])
        st["n"] += 1
        if st["n"] % 60 == 0:
            unreal.log("drive t=%.1f phase=%s pos=%s speed=%.0f" % (t, st["phase"], pawn.get_actor_location(),
                                                                   move.get_forward_speed()))
    except Exception as exc:
        unreal.log_error("quarry drive error: %r" % exc)
        finish("error")


st["handle"] = unreal.register_slate_post_tick_callback(tick)
levels.editor_request_begin_play()
unreal.log("QUARRY DRIVE STARTED")
