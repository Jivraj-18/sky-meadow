"""PIE check that the soldier's ShooterControls really applied (the template Blueprint could
override them): jump count, gravity, camera arm, speeds, and that a triple jump press only jumps once."""
import json
import time

import unreal

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if ues.get_editor_world().get_name() != "Lvl_Quarry":
    levels.load_level("/Game/Maps/Lvl_Quarry")
st = {"t0": None, "jumps": [], "max_count": 0, "handle": None, "report": {}}


def tick(_dt):
    world = ues.get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
    if pawn is None:
        return
    now = time.time()
    if st["t0"] is None:
        st["t0"] = now
        return
    t = now - st["t0"]
    if 1.5 < t < 1.6 and not st["report"]:
        move = pawn.get_movement_component()
        arm = pawn.get_component_by_class(unreal.SpringArmComponent)
        cam = pawn.get_component_by_class(unreal.CameraComponent)
        st["report"] = {"pawn": pawn.get_class().get_name(), "jump_max_count": pawn.get_editor_property("jump_max_count"),
                        "gravity": move.get_editor_property("gravity_scale"), "max_walk_speed": move.get_editor_property("max_walk_speed"),
                        "air_control": move.get_editor_property("air_control"), "arm_length": arm.get_editor_property("target_arm_length"),
                        "socket_offset": [round(v) for v in arm.get_editor_property("socket_offset").to_tuple()],
                        "fov": cam.get_editor_property("field_of_view")}
    # Press jump three times in quick succession (a platformer would triple jump).
    for k, at in enumerate((2.0, 2.3, 2.6)):
        if t > at and k not in st["jumps"]:
            st["jumps"].append(k)
            pawn.jump()
        elif t > at + 0.15:
            pawn.stop_jumping()
    st["max_count"] = max(st["max_count"], pawn.get_editor_property("jump_current_count"))
    if t > 4.0:
        st["report"]["jumps_done_from_3_presses"] = st["max_count"]
        unreal.unregister_slate_post_tick_callback(st["handle"])
        levels.editor_request_end_play()
        unreal.log("SHOOTER VERIFY %s" % json.dumps(st["report"]))


st["handle"] = unreal.register_slate_post_tick_callback(tick)
levels.editor_request_begin_play()
