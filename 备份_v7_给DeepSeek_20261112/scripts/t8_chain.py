import maya.cmds as cmds
import json, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {}

def ancestors(node):
    chain = [node]
    while True:
        p = cmds.listRelatives(chain[-1], parent=True)
        if not p:
            break
        chain.append(p[0])
    return chain

for leaf in ("LeftHand", "LeftFoot", "Head"):
    ch = ancestors(leaf)
    OUT[leaf] = {
        "chain": list(reversed(ch)),
        "world": {n: [round(v, 2) for v in cmds.xform(n, q=True, ws=True, t=True)] for n in ch},
    }

# 逐个祖先试转 Z 60，看手动不动
def try_each(leaf, axis="Z", deg=60):
    chain = ancestors(leaf)[:-1]  # 不含自己
    res = []
    base = cmds.xform(leaf, q=True, ws=True, t=True)
    for n in chain:
        try:
            for j in chain:
                cmds.setAttr(j + ".rotate", 0, 0, 0)
            cur = list(cmds.getAttr(n + ".rotate")[0])
            cur["XYZ".index(axis)] = deg
            cmds.setAttr(n + ".rotate", *cur)
            cmds.refresh(force=True)
            now = cmds.xform(leaf, q=True, ws=True, t=True)
            d = sum((now[i] - base[i]) ** 2 for i in range(3)) ** 0.5
            res.append([n, round(d, 2)])
        except Exception as e:
            res.append([n, "ERR " + str(e)[:40]])
    for j in chain:
        cmds.setAttr(j + ".rotate", 0, 0, 0)
    cmds.refresh(force=True)
    return res

OUT["left_hand_effect"] = try_each("LeftHand")
OUT["left_foot_effect"] = try_each("LeftFoot")
OUT["head_effect"] = try_each("Head")

with open(os.path.join(ROOT, "logs", "t8_chain.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
