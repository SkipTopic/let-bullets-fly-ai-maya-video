# -*- coding: utf-8 -*-
"""Inject via files on disk (avoids commandPort length limit)."""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")
ZC = Path(r"C:\Users\admin\Desktop\MayaProject\MayaTest\zcode_out")
RUN = W / "scripts" / "_chunks"
RUN.mkdir(exist_ok=True)

gen = (W / "scripts" / "p4_generated.py").read_text(encoding="utf-8")
runtime = (ZC / "p4_runtime.py").read_text(encoding="utf-8")
body = gen[len(runtime):]
blocks = re.split(r"\n(?=# ---- S\d+ ----)", body)
print("blocks=%d" % len(blocks))

# write runtime + chunks to disk
(RUN / "runtime.py").write_text(runtime, encoding="utf-8")
chunk_files = []
for i, ch in enumerate(blocks):
    p = RUN / ("chunk_%02d.py" % i)
    p.write_text(ch, encoding="utf-8")
    chunk_files.append(p)

# 1) clean old cameras
r = py('''
import maya.cmds as cmds
P = print
n = 0
for pat in ("CAM_S*", "aimT_S*"):
    for c in cmds.ls(pat) or []:
        try:
            cmds.delete(c); n += 1
        except Exception:
            pass
P("cleaned=%d" % n)
''', timeout=300)
print(r[-120:])

# 2) runtime via file
code = 'import io;exec(io.open(r"%s", encoding="utf-8").read())' % (RUN / "runtime.py")
r = py(code, timeout=600)
print("RUNTIME:", r[-200:])

# 3) chunks via files
ok, fail = 0, []
for i, p in enumerate(chunk_files):
    code = 'import io,traceback\ntry:\n    exec(io.open(r"%s", encoding="utf-8").read())\n    print("CHUNK_OK")\nexcept Exception:\n    print(traceback.format_exc())\n    print("CHUNK_FAIL")' % p
    r = py(code, timeout=900)
    if "CHUNK_OK" in r:
        ok += 1
    else:
        fail.append(i)
        print("chunk %d FAIL:\n%s" % (i, r[-800:]))
print("ok=%d fail=%d %s" % (ok, len(fail), fail))

# 4) save
r = py('''
import maya.cmds as cmds
W = r"%s"
cmds.file(rename=W + "/scenes/p4_final.mb")
cmds.file(save=True, force=True, type="mayaBinary")
print("SAVED p4_final.mb")
''' % W, timeout=600)
print(r[-200:])
