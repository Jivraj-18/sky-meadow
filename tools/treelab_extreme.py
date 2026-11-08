"""Tree Lab, extreme forest sizes only (see treelab_stress.py)."""
import os
g = {"TREELAB_COUNTS": [40000, 90000, 160000, 250000, 490000, 1000000], "TREELAB_PHASES": ["stress"],
     "__name__": "treelab_extreme"}
exec(compile(open(os.path.expanduser("~/unreal-tests/tools/treelab_stress.py")).read(), "treelab_stress.py", "exec"), g)
