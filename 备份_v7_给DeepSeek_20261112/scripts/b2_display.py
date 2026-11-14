import maya.cmds as cmds
import json, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {}

OUT["modelEditors"] = cmds.ls(type="modelEditor") or []
for me in OUT["modelEditors"]:
    try:
        OUT[me] = {
            "wireframeOnShaded": cmds.modelEditor(me, q=True, wireframeOnShaded=True),
            "displayAppearance": cmds.modelEditor(me, q=True, displayAppearance=True),
            "displayTextures": cmds.modelEditor(me, q=True, displayTextures=True),
            "displayLights": cmds.modelEditor(me, q=True, displayLights=True),
            "polymeons": None,
        }
    except Exception as e:
        OUT[me] = repr(e)

# 全局硬件渲染设置
hrg = {}
for attr in ("wireframeOnShaded", "displayEdges", "displayLights", "ssaoEnable",
             "motionBlurEnable", "antiAliasingEnable", "lineCulling"):
    try:
        hrg[attr] = cmds.getAttr("hardwareRenderingGlobals." + attr)
    except Exception:
        hrg[attr] = "N/A"
OUT["hardwareRenderingGlobals"] = hrg

# 材质槽情况
sgs = cmds.ls(type="shadingEngine") or []
OUT["sg_count"] = len(sgs)
sample = []
for sg in sgs[:6]:
    surfs = cmds.sets(sg, q=True) or []
    mats = cmds.listConnections(sg + ".surfaceShader") or []
    sample.append({"sg": sg, "mat": mats[0] if mats else None,
                   "type": cmds.nodeType(mats[0]) if mats else None,
                   "surfaces": len(surfs)})
OUT["sg_sample"] = sample

with open(os.path.join(ROOT, "logs", "b2_display.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
