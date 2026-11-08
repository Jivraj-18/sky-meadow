"""Tree Lab: quality ladder on a one-million-tree forest (see treelab_stress.py)."""
import os
g = {"TREELAB_PHASES": ["quality"], "TREELAB_QUALITY_TREES": 1000000, "__name__": "treelab_max"}
exec(compile(open(os.path.expanduser("~/unreal-tests/tools/treelab_stress.py")).read(), "treelab_stress.py", "exec"), g)
