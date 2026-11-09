#!/usr/bin/env python3
"""Download the free CC0 Poly Haven assets this project uses into assets_src/polyhaven.

They aren't stored in git (size). Run once after cloning, then the import scripts:
  python3 tools/fetch_assets.py
  tools/ue-headless.sh tools/import_quarry_assets.py
  tools/ue-headless.sh tools/import_quarry_plants.py
"""
import json
import os
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets_src", "polyhaven")
TEXTURES = ["rock_face_03", "aerial_grass_rock", "brown_mud_dry"]  # 2k diffuse/normal/rough/arm
MODELS = {                                                 # name: (format, resolution)
    "boulder_01": ("gltf", "1k"), "namaqualand_boulder_02": ("gltf", "1k"), "rock_moss_set_01": ("gltf", "1k"),
    "grass_medium_01": ("gltf", "1k"), "grass_medium_02": ("gltf", "1k"), "grass_bermuda_01": ("gltf", "1k"),
    "dandelion_01": ("gltf", "1k"), "celandine_01": ("gltf", "1k"), "weed_plant_02": ("gltf", "1k"),
    "shrub_03": ("gltf", "1k"), "fern_02": ("gltf", "1k"), "pine_sapling_small": ("gltf", "1k"),
    "fir_sapling": ("gltf", "1k"), "fir_tree_01": ("fbx", "1k"),  # fir_tree_01 is ~240 MB
}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sky-meadow-asset-fetch"}), timeout=600)


def fetch(url, path):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with get(url) as r, open(path, "wb") as fh:
        while chunk := r.read(1 << 20):
            fh.write(chunk)


for name in TEXTURES:
    files = json.load(get("https://api.polyhaven.com/files/" + name))
    for key, label in (("Diffuse", "diff"), ("nor_gl", "nor_gl"), ("Rough", "rough"), ("arm", "arm")):
        if key in files:
            e = files[key]["2k"].get("jpg") or files[key]["2k"]["png"]
            fetch(e["url"], os.path.join(ROOT, name, "%s_%s.%s" % (name, label, e["url"].rsplit(".", 1)[1])))
    print("texture", name)

for name, (fmt, res) in MODELS.items():
    e = json.load(get("https://api.polyhaven.com/files/" + name))[fmt][res][fmt]
    fetch(e["url"], os.path.join(ROOT, name, e["url"].rsplit("/", 1)[1]))
    for rel, inc in e.get("include", {}).items():
        fetch(inc["url"], os.path.join(ROOT, name, rel))
    print("model", name)
