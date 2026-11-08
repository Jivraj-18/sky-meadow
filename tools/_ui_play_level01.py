import importlib, os, sys
sys.path.insert(0, os.path.expanduser("~/unreal-tests/tools"))
import autoplay; importlib.reload(autoplay)
autoplay.SHOW_UI = True
autoplay.CAPTURE_EVERY = 0.2
_start = autoplay.start
autoplay.start = lambda name, route, **kw: _start(name + "_ui", route, **kw)
exec(open(os.path.expanduser("~/unreal-tests/tools/play_level01.py")).read().replace("importlib.reload(autoplay)", ""))
