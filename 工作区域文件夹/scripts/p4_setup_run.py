# -*- coding: utf-8 -*-
"""Fuse scene: SET rebuild + morph hide + sit_all, then inject generated shots in chunks."""
import sys
import base64
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")
ZC = Path(r"C:\Users\admin\Desktop\MayaProject\MayaTest\zcode_out")

p3 = (ZC / "p3_build_set.py").read_text(encoding="utf-8")
m = re.search(r"CODE = r'''(.*?)'''", p3, re.S)
setcode = m.group(1)
# strip file-open / save lines (exact string replace)
kill1 = 'cmds.file(W + r"\scenes\p2_characters.mb", o=True, force=True)'
kill2 = 'cmds.file(rename=W + r"\scenes\p3_set.mb")'
kill3 = 'cmds.file(save=True, force=True, type=\'mayaBinary\')'
setcode = setcode.replace(kill1, "pass")
setcode = setcode.replace(kill2, "pass")
setcode = setcode.replace(kill3, "pass")
assert "p2_characters" not in setcode, "open line not stripped!"
print("setcode stripped OK, len=%d" % len(setcode))

setup = "import maya.cmds as cmds\nP = print\n" + setcode + """

# hide morph top-level meshes via layer
MORPH = ('blink','wink','trouble','gentle','half_eye','keen','laugh','smile','smile2','surprise','serious','anger','pupil','mouth_','eye_up','eye_down','mmd_sdef','FBXASC227')
morphs = []
for t in (cmds.ls(assemblies=True) or []):
    base = t
    for pre in ('p2v2_Huang_', 'p2v2_Shiye_'):
        if t.startswith(pre):
            base = t[len(pre):]
    if any(base == h or base.startswith(h) for h in MORPH):
        morphs.append(t)
if not cmds.objExists('Lyr_morphs'):
    cmds.createNode('displayLayer', name='Lyr_morphs')
cmds.setAttr('Lyr_morphs.visibility', 0)
if morphs:
    cmds.editDisplayLayerMembers('Lyr_morphs', morphs, noRecurse=True)
P('morphs hidden=%d' % len(morphs))
"""

r = py(setup, timeout=900)
print("SETUP:", r[-500:])

runtime = (ZC / "p4_runtime.py").read_text(encoding="utf-8")
gen = (W / "scripts" / "p4_generated.py").read_text(encoding="utf-8")
body = gen[len(runtime):]

blocks = re.split(r"\n(?=# ---- S\d+ ----)", body)
print("blocks=%d" % len(blocks))

# inject runtime first (defines helpers)
b64 = base64.b64encode(runtime.encode("utf-8")).decode("ascii")
r = py('import base64;exec(base64.b64decode("%s").decode("utf-8"))' % b64, timeout=600)
print("RUNTIME:", r[-300:])

CHUNK = 6
for i in range(0, len(blocks), CHUNK):
    chunk = "\n".join(blocks[i:i + CHUNK])
    b64 = base64.b64encode(chunk.encode("utf-8")).decode("ascii")
    r = py('import base64;exec(base64.b64decode("%s").decode("utf-8"))' % b64, timeout=900)
    tail = r[-150:] if r else ""
    print("chunk %d: %s" % (i // CHUNK, tail))
