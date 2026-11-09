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

This repo holds the Unreal Engine 5.7 project (`RealWorldGame/`) and the scripts that built it
(`tools/`). Levels:

| Level | What it is |
|---|---|
| `Maps/Lvl_World1_1` | The game: World 1-1 "Sky Meadow" |
| `Maps/Lvl_Course01` | Earlier test course |

Most content is built by scripts in `tools/` (for example `build_level01.py`) run inside the
editor, so levels can be regenerated and tweaked from code. Everything they place is ordinary
editable content.

### Pieces you add yourself after cloning

Epic template content can't be in a public repo (`Content/Characters`, `Input`, `LevelPrototyping`,
`ThirdPerson`, `Variant_Platforming`, plus their `__ExternalActors__`/`__ExternalObjects__` folders).
Create a new UE 5.7 **Third Person** project (Blueprint) and copy those folders across. Epic's
license lets games ship them, but not publish them as raw files.

Built and tested on Linux with an NVIDIA RTX 2050 (4 GB); see `launch-unreal.sh`.

## Credits

- Made with Unreal Engine 5.7 (© Epic Games).
- 3D models: "Ultimate Platformer Pack" by [Quaternius](https://quaternius.com) (CC0) and
  "Platformer Kit" by [Kenney](https://kenney.nl) (CC0).
- Movement and animation base: Unreal Engine Third Person template (Platforming variant).
- Music, sound effects and HUD icons: original, made for this game.
