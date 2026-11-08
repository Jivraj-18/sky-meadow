#!/usr/bin/env python3
"""Send Python to the running Unreal Editor via the PythonScriptPlugin remote execution.

Usage:
  ue.py -c "print(unreal.SystemLibrary.get_engine_version())"
  ue.py path/to/script.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.expanduser(
    "~/UnrealEngine/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python"))
import remote_execution as rx  # noqa: E402


def run(code, exec_mode=rx.MODE_EXEC_FILE, wait_nodes=15.0):
    cfg = rx.RemoteExecutionConfig()
    cfg.multicast_bind_address = "0.0.0.0"
    remote = rx.RemoteExecution(cfg)
    remote.start()
    try:
        deadline = time.time() + wait_nodes
        while not remote.remote_nodes and time.time() < deadline:
            time.sleep(0.5)
        if not remote.remote_nodes:
            sys.exit("No Unreal Editor found (is it running with remote execution enabled?)")
        remote.open_command_connection(remote.remote_nodes[0]["node_id"])
        result = remote.run_command(code, unattended=True, exec_mode=exec_mode)
        for line in result.get("output", []):
            print(line.get("output", "").rstrip())
        if not result.get("success"):
            print(result.get("result", ""), file=sys.stderr)
            sys.exit(1)
    finally:
        remote.stop()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "-c":
        run(sys.argv[2])  # EXEC_FILE mode also accepts literal multi-line code
    elif len(sys.argv) == 2:
        run(os.path.abspath(sys.argv[1]))
    else:
        sys.exit(__doc__)
