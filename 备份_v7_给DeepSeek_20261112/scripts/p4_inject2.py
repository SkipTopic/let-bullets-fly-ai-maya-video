# -*- coding: utf-8 -*-
import sys
import base64
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")
ZC = Path(r"C:\Users\admin\Desktop\MayaProject\MayaTest\zcode_out")

# clean old shot cameras + stale aimT locators
r = py('''
import maya.cmds as cmds
P = print
n = 0
for c in cmds.ls('CAM_S*') or []:
    try:
        cmds.delete(c); n += 1
    except Exception:
        pass
for c in cmds.ls('aimT_S*') or []:
    try:
        cmds.delete(c); n += 1
    except Exception:
        pass
P('cleaned=%d' % n)
''', timeout=300)
print(r[-200:])

gen = (W / "scripts" / "p4_generated.py").read_text(encoding="utf-8")
runtime = (ZC / "p4_runtime.py").read_text(encoding="utf-8")
body = gen[len(runtime):]
blocks = re.split(r"\n(?=# ---- S\d+ ----)", body)
print("blocks=%d" % len(blocks))

CHUNK = 6
ok, fail = 0, []
for i in range(0, len(blocks), CHUNK):
    chunk = "\n".join(blocks[i:i + CHUNK])
    b64 = base64.b64encode(chunk.encode("utf-8")).decode("ascii")
    code = (
        'import base64,traceback\n'
        'try:\n'
        '    exec(base64.b64decode("%s").decode("utf-8"))\n'
        '    print("CHUNK_OK")\n'
        'except Exception:\n'
        '    print(traceback.format_exc())\n'
        '    print("CHUNK_FAIL")\n' % b64
    )
    r = py(code, timeout=900)
    if "CHUNK_OK" in r:
        ok += 1
        print("chunk %d OK" % (i // CHUNK))
    else:
        fail.append(i // CHUNK)
        print("chunk %d FAIL:\n%s" % (i // CHUNK, r[-900:]))
print("ok=%d fail=%d %s" % (ok, len(fail), fail))
