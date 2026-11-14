# -*- coding: utf-8 -*-
"""One-shot full P4 build: fresh scene -> chars -> SET -> morph hide -> sit -> shots -> verify."""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")
ZC = Path(r"C:\Users\admin\Desktop\MayaProject\MayaTest\zcode_out")
RUN = W / "scripts" / "_chunks"

p3 = (ZC / "p3_build_set.py").read_text(encoding="utf-8")
m = re.search(r"CODE = r'''(.*?)'''", p3, re.S)
setcode = m.group(1)
setcode = setcode.replace('cmds.file(W + r"\scenes\p2_characters.mb", o=True, force=True)', "pass")
setcode = setcode.replace('cmds.file(rename=W + r"\scenes\p3_set.mb")', "pass")
setcode = setcode.replace("cmds.file(save=True, force=True, type='mayaBinary')", "pass")
assert "p2_characters" not in setcode

runtime = (ZC / "p4_runtime.py").read_text(encoding="utf-8")
gen = (W / "scripts" / "p4_generated.py").read_text(encoding="utf-8")
body = gen[len(runtime):]
blocks = re.split(r"\n(?=# ---- S\d+ ----)", body)

RUN.mkdir(exist_ok=True)
(RUN / "runtime.py").write_text(runtime, encoding="utf-8")
for i, ch in enumerate(blocks):
    (RUN / ("chunk_%02d.py" % i)).write_text(ch, encoding="utf-8")

full = r'''
import maya.cmds as cmds
import io
P = print
W = r"{W}"

# 1) fresh scene with the three characters
cmds.file(new=True, force=True)
for tag in ("Ma", "Huang", "Shiye"):
    cmds.loadPlugin("fbxmaya", quiet=True)
    cmds.file(W + "/scenes/p2v2_%s.mb" % tag, i=True, ignoreVersion=True, options="v=0;", pr=True, ra=True)
P("chars imported")

# 2) SET
{setcode}
P("SET built")

# 3) hide morphs
MORPH = ('blink','wink','trouble','gentle','half_eye','keen','laugh','smile','smile2','surprise','serious','anger','pupil','mouth_','eye_up','eye_down','mmd_sdef','FBXASC227')
morphs = []
for t in (cmds.ls(assemblies=True) or []):
    base = t
    for pre in ("p2v2_Huang_", "p2v2_Shiye_"):
        if t.startswith(pre):
            base = t[len(pre):]
    if any(base == h or base.startswith(h) for h in MORPH):
        morphs.append(t)
if not cmds.objExists("Lyr_morphs"):
    cmds.createNode("displayLayer", name="Lyr_morphs")
cmds.setAttr("Lyr_morphs.visibility", 0)
if morphs:
    cmds.editDisplayLayerMembers("Lyr_morphs", morphs, noRecurse=True)
P("morphs hidden=%d" % len(morphs))

# 4) runtime + shots
exec(io.open(r"{RUN}/runtime.py", encoding="utf-8").read())
sit_all()
P("sit done")
'''.replace("{W}", str(W)).replace("{RUN}", str(RUN)).replace("{setcode}", setcode)

r = py(full, timeout=1200)
print("BUILD:", r[-500:])

# 5) shots chunk by chunk
CHUNK = 6
ok, fail = 0, []
for i, p in enumerate(sorted(RUN.glob("chunk_*.py"))):
    if "chunk_71" in p.name or int(p.stem.split("_")[1]) >= len(blocks):
        pass
    code = ('import io,traceback\ntry:\n    exec(io.open(r"%s", encoding="utf-8").read())\n'
            '    print("CHUNK_OK")\nexcept Exception:\n    print(traceback.format_exc())\n    print("CHUNK_FAIL")' % p)
    r = py(code, timeout=900)
    if "CHUNK_OK" in r:
        ok += 1
    else:
        fail.append(p.name)
        print("%s FAIL:\n%s" % (p.name, r[-700:]))
print("chunks ok=%d fail=%d %s" % (ok, len(fail), fail[:5]))

# 6) save
r = py('''
import maya.cmds as cmds
W = r"{W}"
cmds.file(rename=W + "/scenes/p4_final.mb")
cmds.file(save=True, force=True, type="mayaBinary")
P("SAVED")
'''.replace("{W}", str(W)), timeout=600)
print(r[-150:])

# 7) verify frames
r = py('''
import maya.cmds as cmds
P = print
W = r"{W}"
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)
frames = {"S001": 1, "S030": 1268, "S060": 2489}
for name, f in frames.items():
    cam = "CAM_" + name
    if not cmds.objExists(cam):
        P("MISSING " + cam)
        continue
    cmds.modelEditor(mp, e=True, camera=cam)
    cmds.currentTime(f)
    cmds.playblast(frame=[f], format="image", filename=W + "/qa/verify_" + name,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
    P("rendered " + name)
print("VERIFY_DONE")
'''.replace("{W}", str(W)), timeout=900)
print(r[-400:])
