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

## Credits

- Made with Unreal Engine 5.7 (© Epic Games).
- 3D models: "Ultimate Platformer Pack" by [Quaternius](https://quaternius.com) (CC0) and
  "Platformer Kit" by [Kenney](https://kenney.nl) (CC0).
- Movement and animation base: Unreal Engine Third Person template (Platforming variant).
- Music, sound effects and HUD icons: original, made for this game.
