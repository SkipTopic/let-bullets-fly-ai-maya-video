# -*- coding: utf-8 -*-
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")
RUN = W / "scripts" / "_chunks"

gen = (W / "scripts" / "p4_generated.py").read_text(encoding="utf-8")
# strip runtime header: generated file begins with runtime content
runtime = open(W / "scripts" / "_chunks" / "runtime.py", encoding="utf-8").read()
body = gen[len(runtime):]
blocks = re.split(r"\n(?=# ---- S\d+ ----)", body)
for i, ch in enumerate(blocks):
    (RUN / ("chunk_%02d.py" % i)).write_text(ch, encoding="utf-8")
print("blocks=%d" % len(blocks))

r = py('''
import maya.cmds as cmds
P = print
n = 0
for pat in ("CAM_S*", "aimT_S*", "CAM_S*_translate*"):
    for c in cmds.ls(pat) or []:
        try:
            cmds.delete(c); n += 1
        except Exception:
            pass
P("cleaned=%d" % n)
''', timeout=300)
print(r[-120:])

ok, fail = 0, []
for i in range(len(blocks)):
    p = RUN / ("chunk_%02d.py" % i)
    code = ('import io,traceback\ntry:\n    exec(io.open(r"%s", encoding="utf-8").read())\n'
            '    print("CHUNK_OK")\nexcept Exception:\n    print(traceback.format_exc())\n    print("CHUNK_FAIL")' % p)
    r = py(code, timeout=900)
    if "CHUNK_OK" in r:
        ok += 1
    else:
        fail.append(i)
        print("chunk %d FAIL:\n%s" % (i, r[-600:]))
print("ok=%d fail=%d %s" % (ok, len(fail), fail[:6]))

r = py('''
import maya.cmds as cmds
W = r"%s"
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)
frames = {"S001": (1, 1), "S030": (1268, 30), "S060": (2489, 60)}
for name, (f, n) in frames.items():
    cam = "CAM_S%d" %% n
    if not cmds.objExists(cam):
        P("MISSING " + cam)
        continue
    cmds.modelEditor(mp, e=True, camera=cam)
    cmds.currentTime(f)
    cmds.playblast(frame=[f], format="image", filename=W + "/qa/verify_" + name,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
    P("rendered " + name)
cmds.file(save=True, force=True, type="mayaBinary")
print("REVERIFY_DONE")
''' % W, timeout=900)
print(r[-300:])
