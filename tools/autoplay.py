"""Bot playtester for PIE: follows a route of steps, captures frames and the run state.

Usage (inside the editor, see tools/play_*.py):
    import autoplay; autoplay.start("course01", ROUTE)

A route is a list of steps from this module (go, run_jump, wait_platform, ride_platform...).
Each step is called every frame with a Ctx and returns True when finished. Output goes to
Saved/Playtest/<name>/: frames f_NNNNN.png, track.json (position per frame) and result.json.
"""
import json
import os
import time

import unreal

CAPTURE_EVERY = 0.12
SHOW_UI = False  # "shot showui" grabs the whole editor window: slower, but includes the HUD
WARMUP = 2.5
STEP_TIMEOUT = 12.0

level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
project_dir = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
shots_dir = os.path.join(project_dir, "Saved", "Screenshots", "LinuxEditor")


def hud_summary(world):
    """What the on-screen HUD shows right now ('' if there is no platformer HUD)."""
    hud = unreal.GameplayStatics.get_player_controller(world, 0).get_hud()
    widget = hud.get_widget() if isinstance(hud, unreal.PlatformerHUD) else None
    return widget.get_debug_summary() if widget else ""


class Ctx:
    def __init__(self, world, pawn, t, step_t, mem):
        self.world, self.pawn, self.t, self.step_t, self.mem = world, pawn, t, step_t, mem
        self.loc = pawn.get_actor_location()
        self.grounded = not pawn.get_movement_component().is_falling()

    def move_toward(self, x, slow_radius=80.0, lane_y=0.0):
        """Steer to x along the course while holding the centre lane (like a player would)."""
        ix = max(-1.0, min(1.0, (x - self.loc.x) / slow_radius))
        iy = max(-1.0, min(1.0, (lane_y - self.loc.y) / 60.0))
        self.pawn.add_movement_input(unreal.Vector(ix, iy, 0.0), 1.0)

    def press_jump(self):
        self.pawn.jump()
        self.mem["release_at"] = self.t + 0.35

    def actor(self, cls):
        found = unreal.GameplayStatics.get_all_actors_of_class(self.world, cls)
        return found[0] if found else None


# --- Steps ---------------------------------------------------------------------------------

def go(x, tol=25.0):
    """Walk/run to x and stop there on the ground."""
    def step(c):
        c.move_toward(x)
        return c.grounded and abs(c.loc.x - x) < tol
    step.desc = "go %d" % x
    return step


def run_jump(take_off_x, target_x, jumps=2):
    """Run toward target_x, jumping at take_off_x (extra jumps chained in the air)."""
    def step(c):
        # Ease off early in the air: momentum carries a long way with little air braking.
        c.move_toward(target_x, slow_radius=80.0 if c.grounded else 200.0)
        n = c.mem.setdefault("jumps", 0)
        if n == 0 and c.loc.x >= take_off_x:
            c.press_jump(); c.mem["jumps"] = 1; c.mem["last_jump"] = c.t
        elif 0 < n < jumps and c.t - c.mem["last_jump"] > 0.4:
            c.press_jump(); c.mem["jumps"] = n + 1; c.mem["last_jump"] = c.t
        return n >= 1 and c.grounded and c.t - c.mem.get("last_jump", c.t) > 0.3
    step.desc = "run_jump %d->%d" % (take_off_x, target_x)
    return step


def stomp(jump_dx=230.0, max_range=1500.0):
    """Ambush-stomp the nearest live enemy ahead. Jumping while moving gives this character a big
    forward boost (overshoots), so: stand in its path, jump straight up when it walks toward us
    jump_dx away, double jump to hang while it walks under, then nudge onto it and drop."""
    def step(c):
        if "target" not in c.mem:
            ahead = [e for e in unreal.GameplayStatics.get_all_actors_of_class(c.world, unreal.KitEnemy)
                     if not e.is_dead() and -50 < e.get_actor_location().x - c.loc.x < max_range
                     and abs(e.get_actor_location().z - (c.loc.z - 92)) < 150]  # on our level
            if not ahead:
                return True  # already squashed on the way (e.g. landed on it while climbing)
            c.mem["target"] = min(ahead, key=lambda e: e.get_actor_location().x)
            # Wait just inside the near end of its patrol, so it must walk under us.
            start = PATROL_STARTS[c.mem["target"].get_actor_label()]
            near_end = min(start, start + c.mem["target"].get_editor_property("patrol_offset").x)
            c.mem["ambush_x"] = near_end + 40
            c.mem["hold_x"] = c.loc.x
        e = c.mem["target"]
        if not unreal.SystemLibrary.is_valid(e) or e.is_dead():
            c.mem.setdefault("dead_t", c.t)
            c.move_toward(c.loc.x)  # stop and land
            return c.grounded and c.t - c.mem["dead_t"] > 0.3
        ex = e.get_actor_location().x
        dx = ex - c.loc.x
        approaching = ex < c.mem.get("prev_ex", ex)
        c.mem["prev_ex"] = ex
        phase = c.mem.setdefault("phase", "hold")
        c.mem["debug"] = {"ex": round(ex), "phase": phase}
        if phase == "hold":
            # Move up to the ambush spot only while it is walking away or far off.
            if (not approaching or dx > 350) and abs(c.loc.x - c.mem["ambush_x"]) > 20:
                c.mem["hold_x"] = c.mem["ambush_x"]
            c.move_toward(c.mem["hold_x"], slow_radius=120.0)
            still = abs(c.pawn.get_velocity().x) < 80  # a moving jump gets boosted into the enemy
            if c.grounded and still and approaching and dx <= jump_dx:
                c.press_jump(); c.mem["phase"] = "air"; c.mem["jt"] = c.t
        else:  # air: hang with a double jump, gently steer over it; landed without a kill -> retry
            if not c.mem.get("double") and c.t - c.mem["jt"] > 0.35:
                c.press_jump(); c.mem["double"] = True
            nudge = max(-0.3, min(0.3, dx / 100.0)) if c.t - c.mem["jt"] > 0.5 else 0.0
            c.pawn.add_movement_input(unreal.Vector(1.0, 0.0, 0.0), nudge)
            if c.grounded and c.t - c.mem["jt"] > 0.3:
                c.mem["phase"], c.mem["hold_x"], c.mem["double"] = "hold", c.loc.x, False
        return False
    step.desc = "stomp"
    return step


def hop_up(target_x):
    """Climb steps: run toward target_x, jumping every time we touch ground."""
    def step(c):
        c.move_toward(target_x)
        if c.grounded and c.t - c.mem.get("jt", -9) > 0.25 and abs(c.loc.x - target_x) > 40:
            c.press_jump(); c.mem["jt"] = c.t
        return c.grounded and abs(c.loc.x - target_x) < 40
    step.desc = "hop_up %d" % target_x
    return step


def launch_and_land(target_x, air_jump=True):
    """After a jump pad launch: steer to target_x, optional jump at the apex."""
    def step(c):
        c.move_toward(target_x, slow_radius=150.0)
        vz = c.pawn.get_velocity().z
        if not c.grounded:
            c.mem["airborne"] = True
            if air_jump and not c.mem.get("air_jumped") and vz < 50:
                c.press_jump(); c.mem["air_jumped"] = True
        return c.mem.get("airborne") and c.grounded and abs(c.loc.x - target_x) < 60
    step.desc = "launch_and_land %d" % target_x
    return step


def wait_platform(cls, max_x):
    """Hold position until the platform's x is at or below max_x (near our side)."""
    def step(c):
        c.move_toward(c.mem.setdefault("hold_x", c.loc.x))
        p = c.actor(cls)
        return p is not None and p.get_actor_location().x <= max_x
    step.desc = "wait_platform x<=%d" % max_x
    return step


def board_platform(cls, take_off_x, jumps=2):
    """Run at the platform, jump at take_off_x (chaining air jumps) and centre on it."""
    def step(c):
        p = c.actor(cls)
        px = p.get_actor_location().x
        c.move_toward(px, slow_radius=60.0)
        n = c.mem.setdefault("jumps", 0)
        if n == 0 and c.loc.x >= take_off_x:
            c.press_jump(); c.mem["jumps"] = 1; c.mem["jt"] = c.t
        elif 0 < n < jumps and c.t - c.mem["jt"] > 0.4:
            c.press_jump(); c.mem["jumps"] = n + 1; c.mem["jt"] = c.t
        return n >= 1 and c.t - c.mem["jt"] > 0.3 and c.grounded and abs(c.loc.x - px) < 80
    step.desc = "board_platform jump@%d" % take_off_x
    return step


def ride_platform(cls, until_x):
    """Stay centred on the platform until it reaches until_x."""
    def step(c):
        p = c.actor(cls)
        px = p.get_actor_location().x
        c.move_toward(px, slow_radius=60.0)
        return px >= until_x
    step.desc = "ride_platform until %d" % until_x
    return step


def reach_goal(x):
    """Head for the goal flag until the level registers as complete."""
    def step(c):
        c.move_toward(x)
        run = unreal.PlatformerSubsystem.get(c.world)
        return run is not None and run.is_level_complete() and c.step_t > 1.0  # linger for the video
    step.desc = "reach_goal %d" % x
    return step


def fall_off_side():
    """Deliberately walk off the course sideways until the kill zone respawns us."""
    def step(c):
        c.pawn.add_movement_input(unreal.Vector(0.0, 1.0, 0.0), 1.0)
        run = unreal.PlatformerSubsystem.get(c.world)
        respawned = run.get_respawn_count() > c.mem.setdefault("respawns0", run.get_respawn_count())
        return respawned or run.is_game_over()  # the last life ends the game without a respawn
    step.desc = "fall_off_side"
    return step


def expect_near(x, tol=150.0):
    """Assert the pawn is near x (e.g. respawned at a checkpoint); fails the run otherwise."""
    def step(c):
        if c.step_t < 0.5:
            return False
        if abs(c.loc.x - x) > tol:
            raise AssertionError("expected x~%d, pawn at x=%d" % (x, c.loc.x))
        return True
    step.desc = "expect_near %d" % x
    return step


def expect_lives(n):
    def step(c):
        lives = unreal.PlatformerSubsystem.get(c.world).get_lives()
        if lives != n:
            raise AssertionError("expected %d lives, have %d" % (n, lives))
        return True
    step.desc = "expect_lives %d" % n
    return step


def expect_game_over():
    def step(c):
        if not unreal.PlatformerSubsystem.get(c.world).is_game_over():
            raise AssertionError("expected game over")
        return True
    step.desc = "expect_game_over"
    return step


def view_from(camera_label, seconds=2.0):
    """Photo mode: look through a CameraActor (by label) for a while; frames keep capturing."""
    def step(c):
        if "cam" not in c.mem:
            cams = [a for a in unreal.GameplayStatics.get_all_actors_of_class(c.world, unreal.CameraActor)
                    if a.get_actor_label() == camera_label]
            if not cams:
                raise AssertionError("no camera " + camera_label)
            c.mem["cam"] = cams[0]
            unreal.GameplayStatics.get_player_controller(c.world, 0).set_view_target_with_blend(cams[0], 0.0)
        return c.step_t >= seconds
    step.desc = "view_from %s" % camera_label
    return step


def expect_hud(text):
    """Assert the on-screen HUD shows text (see PlatformerHUDWidget.GetDebugSummary)."""
    def step(c):
        if c.step_t < 0.3:  # let the HUD catch up this frame
            return False
        shown = hud_summary(c.world)
        if text not in shown:
            raise AssertionError("HUD missing %r: %s" % (text, shown))
        return True
    step.desc = "expect_hud %r" % text
    return step


def wait(seconds):
    def step(c):
        return c.step_t >= seconds
    step.desc = "wait %.1f" % seconds
    return step


# --- Runner --------------------------------------------------------------------------------

PATROL_STARTS = {}  # enemy label -> patrol start x, read from the editor level before play


def start(name, route, stop_on_fall=True):
    out_dir = os.path.join(project_dir, "Saved", "Playtest", name)
    os.makedirs(out_dir, exist_ok=True)
    for d in (out_dir, shots_dir):
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith((".png", ".json")):
                    os.remove(os.path.join(d, f))

    PATROL_STARTS.clear()
    for e in unreal.GameplayStatics.get_all_actors_of_class(editor.get_editor_world(), unreal.KitEnemy):
        PATROL_STARTS[e.get_actor_label()] = e.get_actor_location().x

    st = {"t0": None, "last_cap": -1.0, "frame": 0, "track": [], "step": 0,
          "step_t0": None, "mem": {}, "log": [], "handle": None, "done": False}

    def finish(reason, world=None):
        if st["done"]:
            return
        st["done"] = True
        unreal.unregister_slate_post_tick_callback(st["handle"])
        result = {"reason": reason, "steps_done": st["step"], "steps_total": len(route), "log": st["log"]}
        try:
            run = unreal.PlatformerSubsystem.get(world) if world is not None else None
            if run:
                result.update(coins=run.get_coins(), lives=run.get_lives(), game_over=run.is_game_over(),
                              level_complete=run.is_level_complete(),
                              respawns=run.get_respawn_count())
            result["hud"] = hud_summary(world) if world is not None else ""
        except Exception as exc:  # still save frames and track below
            result["state_error"] = repr(exc)
        if os.path.isdir(shots_dir):
            for i, f in enumerate(sorted(f for f in os.listdir(shots_dir) if f.startswith("ScreenShot"))):
                os.replace(os.path.join(shots_dir, f), os.path.join(out_dir, "f_%05d.png" % i))
        json.dump(st["track"], open(os.path.join(out_dir, "track.json"), "w"))
        json.dump(result, open(os.path.join(out_dir, "result.json"), "w"), indent=1)
        level_editor.editor_request_end_play()
        unreal.log("PLAYTEST DONE %s" % json.dumps(result))

    def tick(_dt):
        if st["done"]:
            return
        world = None
        try:
            world = editor.get_game_world()
            pawn = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
            if pawn is None:
                return
            now = time.time()
            if st["t0"] is None:
                st["t0"] = now + WARMUP
            t = now - st["t0"]
            if t < 0:  # warm-up: not moving yet, but record it (title card)
                if now - st.setdefault("last_warm_cap", 0.0) >= CAPTURE_EVERY:
                    st["last_warm_cap"] = now
                    unreal.SystemLibrary.execute_console_command(world, "shot showui" if SHOW_UI else "shot")
                return
            if st["step_t0"] is None:
                st["step_t0"] = t

            ctx = Ctx(world, pawn, t, t - st["step_t0"], st["mem"])
            if "release_at" in st["mem"] and t >= st["mem"]["release_at"]:
                pawn.stop_jumping(); del st["mem"]["release_at"]

            # A respawn means the bot fell into a kill zone: stop and report where.
            run = unreal.PlatformerSubsystem.get(world)
            if stop_on_fall and run and run.get_respawn_count() > 0:
                last = st["track"][-1] if st["track"] else {}
                st["log"].append("%.1fs LOST A LIFE (fell or hit) during %s (last seen x=%s z=%s)" % (
                    t, route[st["step"]].desc, last.get("x"), last.get("z")))
                finish("fell", world)
                return

            step = route[st["step"]]
            if step(ctx):
                st["log"].append("%.1fs ok   %s" % (t, step.desc))
                st["step"] += 1
                st["step_t0"], st["mem"] = t, {}
                if st["step"] >= len(route):
                    finish("route complete", world)
                    return
            elif ctx.step_t > STEP_TIMEOUT:
                st["log"].append("%.1fs FAIL %s (timeout at x=%d z=%d)" % (t, step.desc, ctx.loc.x, ctx.loc.z))
                finish("step timeout", world)
                return

            if t - st["last_cap"] >= CAPTURE_EVERY:
                st["last_cap"] = t
                # "shot" reuses the viewport; HighResShot allocates per call and exhausts 4 GB VRAM.
                unreal.SystemLibrary.execute_console_command(world, "shot showui" if SHOW_UI else "shot")
                st["track"].append({"t": round(t, 2), "x": round(ctx.loc.x), "y": round(ctx.loc.y),
                                    "z": round(ctx.loc.z), "air": not ctx.grounded, "step": st["step"],
                                    **st["mem"].get("debug", {})})
                fx = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.KitEffect)
                if fx:
                    st["track"][-1]["fx"] = sorted(set(e.get_class().get_name().replace("BP_FX_", "").replace("_C", "") for e in fx))
                animator = pawn.get_component_by_class(unreal.KitCharacterAnimator)
                if animator:
                    st["track"][-1]["anim"] = animator.get_current_anim_name().replace("CharacterCharacterArmature_", "")
                if st["frame"] % 4 == 0:
                    st["track"][-1]["hud"] = hud_summary(world)
                st["frame"] += 1
        except Exception as exc:  # never leave a broken tick callback registered
            unreal.log_error("autoplay error: %r" % exc)
            finish("error: %r" % exc, world)

    unreal.SystemLibrary.execute_console_command(editor.get_editor_world(), "scalability 1")
    st["handle"] = unreal.register_slate_post_tick_callback(tick)
    level_editor.editor_request_begin_play()
    unreal.log("PLAYTEST STARTED %s (%d steps)" % (name, len(route)))
