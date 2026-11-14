import maya.cmds as cmds
import maya.api.OpenMaya as om
import json, os, math

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {}
for name, a, b in (
    ("x_to_y", [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]),
    ("down_to_forward", [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]),
):
    va = om.MVector(*a).normal()
    vb = om.MVector(*b).normal()
    q = om.MQuaternion(va, vb)
    OUT[name] = {
        "q": [q.x, q.y, q.z, q.w],
        "a_times_qmatrix": list(va * q.asMatrix()),
        "b_times_qmatrix": list(vb * q.asMatrix()),
        "inverse": list(va * q.inverted().asMatrix()),
    }

cmds.file(new=True, f=True)
cmds.select(clear=True)
a = cmds.joint(p=(0.0, 0.0, 0.0), name="J_A")
b = cmds.joint(p=(0.0, 10.0, 0.0), name="J_B")
c = cmds.joint(p=(0.0, 20.0, 0.0), name="J_C")
cmds.joint(a, e=True, oj="xyz", sao="yup")
cmds.currentTime(1)
cmds.refresh(force=True)
current = (om.MVector(*cmds.xform(b, q=True, ws=True, t=True)) - om.MVector(*cmds.xform(a, q=True, ws=True, t=True))).normal()
desired = om.MVector(1.0, 0.0, 0.0)
delta = om.MQuaternion(current, desired)
world = om.MTransformationMatrix(om.MMatrix(cmds.xform(a, q=True, ws=True, m=True)))
old_q = world.rotation(asQuaternion=True)
results = {}
for label, new_q in (("pre", delta * old_q), ("post", old_q * delta), ("pre_inverse", delta.inverted() * old_q), ("post_inverse", old_q * delta.inverted())):
    euler = new_q.asEulerRotation()
    cmds.xform(a, ws=True, ro=[math.degrees(euler.x), math.degrees(euler.y), math.degrees(euler.z)])
    cmds.refresh(force=True)
    results[label] = {"child": list(cmds.xform(b, q=True, ws=True, t=True)), "local_rotate": list(cmds.getAttr(a + ".rotate")[0])}
    cmds.xform(a, ws=True, ro=[0.0, 0.0, 0.0])
    cmds.refresh(force=True)
OUT["joint_test"] = results
OUT["initial_current"] = list(current)
OUT["initial_joint_orient"] = list(cmds.getAttr(a + ".jointOrient")[0])
with open(os.path.join(ROOT, "logs", "q3d_math_probe.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
