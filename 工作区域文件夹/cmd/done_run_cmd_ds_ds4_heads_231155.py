"""DS 量头：用 OpenMaya 取每人头部/肩部实际包围盒，供离线构图计算使用。"""
import json
import os

import maya.api.OpenMaya as om
import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"

CHARS = {
    "Ma": {"mesh": "NH_MaleM_140_LOD0", "head": "Bip001Head", "clavL": "Bip001LClavicle", "clavR": "Bip001RClavicle"},
    "Huang": {"mesh": "Huang_AragakiFBXASC032Shinjiro_mesh", "head": "Huang_Head", "clavL": "Huang_LeftShoulder", "clavR": "Huang_RightShoulder"},
    "Shiye": {"mesh": "Shiye_JunpeiFBXASC032Iori_mesh", "head": "Shiye_Head", "clavL": "Shiye_LeftShoulder", "clavR": "Shiye_RightShoulder"},
}


def verts_world(mesh):
    sel = om.MSelectionList()
    sel.add(mesh)
    dag = sel.getDagPath(0)
    fn = om.MFnMesh(dag)
    pts = fn.getPoints(om.MSpace.kWorld)
    return pts


out = {"errors": [], "chars": {}}

for name, spec in CHARS.items():
    entry = {"mesh": spec["mesh"]}
    try:
        hv = cmds.xform(spec["head"], q=True, ws=True, t=True)
        head = om.MVector(hv[0], hv[1], hv[2])
        pts = verts_world(spec["mesh"])
        # 头部：距 head 关节 13cm 内的顶点
        head_pts = [p for p in pts if (p - head).length() < 13.0]
        if head_pts:
            xs = [p.x for p in head_pts]
            ys = [p.y for p in head_pts]
            zs = [p.z for p in head_pts]
            entry["head_bbox"] = [round(min(xs), 2), round(min(ys), 2), round(min(zs), 2),
                                  round(max(xs), 2), round(max(ys), 2), round(max(zs), 2)]
            entry["head_count"] = len(head_pts)
            entry["head_center"] = [round((min(xs) + max(xs)) / 2, 2), round((min(ys) + max(ys)) / 2, 2),
                                    round((min(zs) + max(zs)) / 2, 2)]
            entry["head_size"] = [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2), round(max(zs) - min(zs), 2)]
        # 肩宽：两锁骨中点上下 14cm 的顶点
        cl = cmds.xform(spec["clavL"], q=True, ws=True, t=True)
        cr = cmds.xform(spec["clavR"], q=True, ws=True, t=True)
        mid = om.MVector((cl[0] + cr[0]) / 2, (cl[1] + cr[1]) / 2, (cl[2] + cr[2]) / 2)
        band = [p for p in pts if abs(p.y - mid.y) < 14.0]
        if band:
            xs = [p.x for p in band]
            zs = [p.z for p in band]
            entry["shoulder_band"] = {"y_mid": round(mid.y, 2), "x": [round(min(xs), 2), round(max(xs), 2)],
                                      "z": [round(min(zs), 2), round(max(zs), 2)], "count": len(band)}
        entry["head_joint"] = [round(v, 2) for v in hv]
    except Exception as exc:  # noqa: BLE001
        out["errors"].append("%s: %r" % (name, exc))
    out["chars"][name] = entry

path = os.path.join(ROOT, "logs", "ds4_heads.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
