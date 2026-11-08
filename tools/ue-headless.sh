#!/usr/bin/env bash
# Run a Python script in a headless editor (no GPU use): tools/ue-headless.sh script.py
# The interactive editor must be closed — two editors on one project conflict.
set -e
if pidof UnrealEditor >/dev/null; then echo "Close the Unreal Editor first" >&2; exit 1; fi
SCRIPT="$(realpath "$1")"
"$HOME/UnrealEngine/Engine/Binaries/Linux/UnrealEditor-Cmd" \
  "$HOME/unreal-tests/RealWorldGame/RealWorldGame.uproject" \
  -run=pythonscript -script="$SCRIPT" \
  -nullrhi -unattended -nosplash -nopause -stdout -FullStdOutLogOutput 2>&1 \
  | grep -E "LogPython|Error|error:|Fatal" | grep -vE "DeprecationWarning|^\s*$"
