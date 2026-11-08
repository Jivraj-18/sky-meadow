"""Print size (cm) of key kit meshes and list animations, to plan scaling and blocks."""
import unreal

lib = unreal.EditorAssetLibrary
for path in lib.list_assets("/Game/Kit", recursive=True, include_folder=False):
    data = lib.find_asset_data(path)
    cls = str(data.asset_class_path.asset_name)
    name = str(data.asset_name)
    if cls == "StaticMesh":
        mesh = unreal.load_asset(path)
        box = mesh.get_bounding_box()
        size = box.max - box.min
        print("SM %-40s %5.0f x %5.0f x %5.0f  min_z=%5.0f  %s" % (
            name, size.x, size.y, size.z, box.min.z, path.rsplit("/", 2)[-2]))
    elif cls == "SkeletalMesh":
        mesh = unreal.load_asset(path)
        b = mesh.get_bounds()
        print("SK %-40s extent %s  %s" % (name, b.box_extent, path))
    elif cls == "AnimSequence" and ("/Character/" in path or "/Enemies/" in path):
        print("AN", path)
