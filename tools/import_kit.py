"""Import the Quaternius Ultimate Platformer kit FBX files into /Game/Kit/<Category>."""
import os

import unreal

SRC = os.path.expanduser(
    "~/unreal-tests/assets_src/quaternius_platformer/Platformer Game Kit - Dec 2021")
CATEGORIES = {
    "Character/FBX": "/Game/Kit/Character",
    "Enemies/FBX": "/Game/Kit/Enemies",
    "Powerups and Pickups/FBX": "/Game/Kit/Pickups",
    "Level and Mechanics/FBX": "/Game/Kit/Level",
    "Nature/FBX": "/Game/Kit/Nature",
    "Cubes/FBX": "/Game/Kit/Cubes",
    "Modular Platforms/Single Height/FBX": "/Game/Kit/Platforms/SingleHeight",
    "Modular Platforms/3D/FBX": "/Game/Kit/Platforms/3D",
    "Modular Platforms/2D/FBX": "/Game/Kit/Platforms/2D",
    "Modular Platforms/Single Cube/FBX": "/Game/Kit/Platforms/SingleCube",
}

# Rigged models share bone names; one folder each stops Interchange merging their skeletons.
OWN_FOLDER = {"/Game/Kit/Character", "/Game/Kit/Enemies"}

# Call Interchange directly: AssetTools.import_asset_tasks syncs the Content Browser
# afterwards, which asserts in a headless (-nullrhi) commandlet.
manager = unreal.InterchangeManager.get_interchange_manager_scripted()
files, failed = 0, []
for sub, dest in CATEGORIES.items():
    folder = os.path.join(SRC, sub)
    if not os.path.isdir(folder):
        unreal.log_warning("missing folder %s" % folder)
        continue
    for f in sorted(os.listdir(folder)):
        if not f.lower().endswith(".fbx"):
            continue
        files += 1
        target = dest + "/" + f[:-4] if dest in OWN_FOLDER else dest
        # Animated props (chest, door, lever...) also clash on skeletons in a shared
        # folder, so a failed import is retried once in its own folder.
        for attempt in (target, dest + "/" + f[:-4]):
            params = unreal.ImportAssetParameters()
            params.is_automated = True
            params.replace_existing = True
            source = unreal.InterchangeManager.create_source_data(os.path.join(folder, f))
            try:
                ok = manager.import_asset(attempt, source, params)
            except RuntimeError as exc:
                unreal.log_warning("import %s -> %s: %s" % (f, attempt, exc))
                ok = False
            if ok or attempt != target:
                break
        if not ok:
            failed.append(f)

unreal.EditorAssetLibrary.save_directory("/Game/Kit", only_if_is_dirty=False, recursive=True)
count = len(unreal.EditorAssetLibrary.list_assets("/Game/Kit", recursive=True))
print("files:", files, "assets in /Game/Kit:", count, "failed:", failed)
