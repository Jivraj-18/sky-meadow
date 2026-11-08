#!/usr/bin/env bash
# Launch Unreal Editor on the NVIDIA RTX 2050 (laptop defaults to Intel graphics).
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
export __VK_LAYER_NV_optimus=NVIDIA_only
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json
PROJECT="${1:-$HOME/unreal-tests/RealWorldGame/RealWorldGame.uproject}"
exec "$HOME/UnrealEngine/Engine/Binaries/Linux/UnrealEditor" "$PROJECT" "${@:2}"
