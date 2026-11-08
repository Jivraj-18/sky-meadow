"""Quarry performance check: turn Nanite off for small plants (classic instancing is cheaper for
masked grass), then measure PIE frame rate at Medium and at Epic+Lumen from the PlayerStart."""
import time

import unreal

lib = unreal.EditorAssetLibrary
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
TREES = ("fir_tree_01",)

changed = 0
for path in lib.list_assets("/Game/Quarry", recursive=True, include_folder=False):
    if any(t in path for t in TREES):
        continue
    asset = unreal.load_asset(path)
    if isinstance(asset, unreal.StaticMesh):
        ns = asset.get_editor_property("nanite_settings")
        if ns.get_editor_property("enabled") and ("/Plants/" in path or "grass" in path):
            ns.set_editor_property("enabled", False)
            asset.set_editor_property("nanite_settings", ns)
            lib.save_loaded_asset(asset, only_if_is_dirty=False)
            changed += 1
unreal.log("QUARRY PERF nanite off for %d plant meshes" % changed)

if ues.get_editor_world().get_name() != "Lvl_Quarry":
    levels.load_level("/Game/Maps/Lvl_Quarry")

SETTINGS = [("Medium", ["scalability 1", "r.DynamicGlobalIlluminationMethod 0", "r.ReflectionMethod 2", "r.Shadow.Virtual.Enable 0"]),
            ("Epic + Lumen + VSM", ["scalability 3", "r.DynamicGlobalIlluminationMethod 1", "r.ReflectionMethod 1", "r.Shadow.Virtual.Enable 1"])]
st = {"i": 0, "t0": None, "dts": [], "handle": None}


def tick(dt):
    world = ues.get_game_world()
    if world is None or unreal.GameplayStatics.get_player_pawn(world, 0) is None:
        return
    now = time.time()
    if st["t0"] is None:
        for c in SETTINGS[st["i"]][1]:
            unreal.SystemLibrary.execute_console_command(world, c)
        st["t0"] = now
        return
    if now - st["t0"] > 3.0:  # settle 3 s, then measure 5 s
        st["dts"].append(dt)
    if now - st["t0"] > 8.0:
        fps = len(st["dts"]) / sum(st["dts"])
        unreal.log("QUARRY PERF %s fps=%.1f" % (SETTINGS[st["i"]][0], fps))
        st.update(i=st["i"] + 1, t0=None, dts=[])
        if st["i"] >= len(SETTINGS):
            unreal.unregister_slate_post_tick_callback(st["handle"])
            levels.editor_request_end_play()
            unreal.SystemLibrary.execute_console_command(ues.get_editor_world(), "scalability 1")
            unreal.log("QUARRY PERF DONE")


st["handle"] = unreal.register_slate_post_tick_callback(tick)
levels.editor_request_begin_play()
