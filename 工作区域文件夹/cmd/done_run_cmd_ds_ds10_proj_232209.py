"""用 Maya 自己的 M3dView 投影做 A/B 对照，确认视口实际看到的画面比例。"""
import json
import os

import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om2
import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
out = {"errors": [], "points": {}}
panel = "modelPanel4"

view = omui.M3dView()
omui.M3dView.getM3dViewFromModelPanel(panel, view)
out["view_width"] = view.portWidth()
out["view_height"] = view.portHeight()

PTS = {
    "Ma_head": (0.02, 113.05, -105.24),
    "Ma_top": (0.02, 124.97, -105.24),
    "Huang_head": (90.39, 123.19, 51.87),
    "Shiye_head": (-89.20, 123.49, 51.37),
    "table_center": (0.0, 75.8, 0.0),
    "table_near": (0.0, 75.8, 88.0),
}
for name, p in PTS.items():
    pt = om2.MPoint(p[0], p[1], p[2])
    x = view.worldToView(pt, omui.M3dView.kWorld)
    out["points"][name] = {"x": round(x[0], 1), "y": round(x[1], 1)}

out["camera"] = cmds.modelEditor(panel, q=True, camera=True)

with open(os.path.join(ROOT, "logs", "ds10_proj.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
