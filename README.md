# Sky Meadow

A small 3D platformer made with Unreal Engine 5.7. Run, jump and stomp your way across a floating
sky meadow: collect coins, reach the checkpoints and touch the goal flag.

https://github.com/Jivraj-18/sky-meadow/raw/main/media/sky-meadow-gameplay.mp4

▶ [Watch the gameplay video](media/sky-meadow-gameplay.mp4) (30 s, with sound)

## Download and play

**[Download the latest release](https://github.com/Jivraj-18/sky-meadow/releases/latest)** — Linux x86_64.

1. Download `SkyMeadow-v0.1.0-Linux.zip` and unzip it.
2. Run `./RealWorldGame.sh` inside the `SkyMeadow` folder.

Needs a GPU with Vulkan support and current drivers (tested on an NVIDIA RTX 2050, 4 GB).
On NVIDIA laptops with hybrid graphics, if the game starts on the integrated GPU:

```sh
__NV_PRIME_RENDER_OFFLOAD=1 __VK_LAYER_NV_optimus=NVIDIA_only ./RealWorldGame.sh
```

## Controls

| Key | Action |
|---|---|
| W A S D | Move |
| Mouse | Look |
| Space | Jump (up to 3 times in the air) |
| Shift | Dash |
| R | Restart the level |
| Esc | Quit |

## Features

- World 1-1 "Sky Meadow": stepping-stone islands, a brick staircase, a jump pad, a moving platform
  and two checkpoints
- Enemies to stomp: crab, monster, skull and bee
- 3 lives, checkpoints, game over and restart
- HUD with hearts, coin counter, timer and a level complete screen
- Original chiptune music and sound effects
- Cartoon effects: coin sparkles, stomp puffs, landing dust

## Source code

This repo also holds the Unreal Engine 5.7 project (`RealWorldGame/`) and the scripts that built it
(`tools/`). Levels:

| Level | What it is |
|---|---|
| `Maps/Lvl_World1_1` | The game: Sky Meadow (cartoon platformer) |
| `Maps/Lvl_Quarry` | [Quarry Ridge](https://github.com/Jivraj-18/quarry-ridge): realistic quarry with a soldier, a dirt road and a drivable car (work in progress) |
| `Maps/Lvl_TreeLab` | Tree rendering experiment (Procedural Vegetation Editor trees) |

Most content is built by scripts in `tools/` (for example `build_level01.py`, `build_quarry.py`) run
inside the editor, so levels can be regenerated and tweaked from code. Everything they place is
ordinary editable content (actors, Landscape, Foliage).

### Pieces you add yourself after cloning

Some files can't be in a public repo:

1. **Epic template content** (`Content/Characters`, `Input`, `LevelPrototyping`, `ThirdPerson`,
   `Variant_Platforming`): create a new UE 5.7 **Third Person** project (Blueprint) and copy those
   folders across. Epic's license lets games ship them, not publish them as raw files.
2. **Poly Haven assets** (CC0, too big for git): `python3 tools/fetch_assets.py`, then
   `tools/ue-headless.sh tools/import_quarry_assets.py` and `tools/import_quarry_plants.py`.
3. **Mixamo soldier** (free, but not redistributable as raw files): download "Swat" and the
   animations listed in `tools/import_soldier.py` from [mixamo.com](https://www.mixamo.com) into
   `assets_src/mixamo/`, then run that script in the editor.
4. **Epic vehicle template** (`Content/VehicleTemplate`, `Content/Vehicles`): copy
   `Templates/TP_VehicleAdvBP/Content/VehicleTemplate` and
   `Templates/TemplateResources/Standard/Vehicles/Content` from the engine into `Content/`.

Built and tested on Linux with an NVIDIA RTX 2050 (4 GB); see `launch-unreal.sh`.

## Credits

- Made with Unreal Engine 5.7 (© Epic Games).
- 3D models: "Ultimate Platformer Pack" by [Quaternius](https://quaternius.com) (CC0) and
  "Platformer Kit" by [Kenney](https://kenney.nl) (CC0).
- Movement and animation base: Unreal Engine Third Person template (Platforming variant).
- Music, sound effects and HUD icons: original, made for this game.
- Quarry scene: textures, rocks and plants from [Poly Haven](https://polyhaven.com) (CC0); soldier
  character and animations from [Mixamo](https://www.mixamo.com) (Adobe, not included in the repo);
  reference frames in `reference/` are from the "PUBG MOBILE - Erangel's New Imagination Plaza"
  trailer by PUBG MOBILE (CC BY 3.0, via Wikimedia Commons).
