"""Photo mode: side views of each enemy type via temporary cameras (not saved in the level)."""
import importlib
import os
import sys

import unreal

sys.path.insert(0, os.path.expanduser("~/unreal-tests/tools"))
import autoplay  # noqa: E402
importlib.reload(autoplay)
from autoplay import view_from  # noqa: E402

actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SHOTS = {  # label: (camera location, rotation pitch/yaw) - side views from -Y looking +Y
    "Cam_Crab": ((850, -330, 160), (-12, 90)),
    "Cam_Monster": ((3825, -330, 560), (-12, 90)),
    "Cam_Skull": ((4750, -300, 900), (-12, 90)),
    "Cam_Bee": ((7025, -380, 1360), (-5, 90)),
}
for a in actors.get_all_level_actors():
    if a.get_actor_label().startswith("Cam_"):
        actors.destroy_actor(a)
for label, ((x, y, z), (pitch, yaw)) in SHOTS.items():
    cam = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(x, y, z), unreal.Rotator(0, pitch, yaw))
    cam.set_actor_label(label)

autoplay.start("photo_enemies", [view_from(label, 1.5) for label in SHOTS], stop_on_fall=False)
