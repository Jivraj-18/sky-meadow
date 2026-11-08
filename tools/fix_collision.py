"""Give every kit static mesh collision (the FBX import created none).

Cube-shaped blocks get a box; everything else collides with its own triangles.
"""
import unreal

lib = unreal.EditorAssetLibrary
sm_lib = unreal.EditorStaticMeshLibrary
BOX_FOLDERS = ("/Game/Kit/Cubes/", "/Game/Kit/Platforms/")

boxed = complex_ = 0
for path in lib.list_assets("/Game/Kit", recursive=True, include_folder=False):
    data = lib.find_asset_data(path)
    if str(data.asset_class_path.asset_name) != "StaticMesh":
        continue
    mesh = unreal.load_asset(path)
    if path.startswith(BOX_FOLDERS):
        sm_lib.remove_collisions(mesh)
        sm_lib.add_simple_collisions(mesh, unreal.ScriptCollisionShapeType.BOX)
        boxed += 1
    else:
        mesh.get_editor_property("body_setup").set_editor_property(
            "collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        complex_ += 1
    lib.save_loaded_asset(mesh, only_if_is_dirty=False)

print("COLLISION FIXED box=%d complex_as_simple=%d" % (boxed, complex_))
