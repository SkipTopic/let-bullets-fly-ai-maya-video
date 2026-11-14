import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
LOG = os.path.join(ROOT, "logs", "n2.json")
OUT = {"errors": []}
def dump(): json.dump(OUT, open(LOG,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
def shoot(tag, cam, f=1):
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(f); cmds.lookThru(p, cam)
    for old in os.listdir(REV):
        if old.startswith("NW_"+tag+"."):
            try: os.remove(os.path.join(REV, old))
            except Exception: pass
    cmds.playblast(frame=f, format="image", filename=os.path.join(REV,"NW_"+tag),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(854,480), quality=95,
                   compression="png")
try:
    cmds.file(os.path.join(ROOT,"scenes","手工摆位_v9_newma.mb"), o=True, force=True)
    # 右臂回到自然下垂
    for b in ("Bip001RUpperArm","Bip001RForeArm","Bip001RHand"):
        if cmds.objExists(b):
            cmds.setAttr(b+".rotate", 0,0,0)
    cmds.refresh(force=True)

    shots = json.load(open(os.path.join(ROOT,"shots_varied.json"), encoding="utf-8"))
    heads = {"Ma": cmds.xform("Bip001Head", q=True, ws=True, t=True),
             "Huang": cmds.xform("Huang_Head", q=True, ws=True, t=True),
             "Shiye": cmds.xform("Shiye_Head", q=True, ws=True, t=True)}
    OUT["heads"] = {k:[round(v,1) for v in p] for k,p in heads.items()}
    if cmds.objExists("CAMERAS"):
        kids = cmds.listRelatives("CAMERAS", children=True) or []
        if kids:
            cmds.delete(kids)
    grp = "CAMERAS" if cmds.objExists("CAMERAS") else cmds.group(em=True, name="CAMERAS")
    cmap = {}
    for s in shots:
        h = heads[s["subject"]]
        dist = s["dist"]
        k = dist / max(s["dist"], 1.0)
        cam = cmds.camera(name=s["id"]+"_C", focalLength=s["focal"])[0]
        cmap[s["id"]] = cam
        cmds.setAttr(cam+".translate", s["eye0"][0], h[1]+s["hrel"], s["eye0"][2])
        loc = cmds.spaceLocator(name="A_"+s["id"])[0]
        cmds.setAttr(loc+".translate", h[0], h[1]-3.0, h[2])
        c = cmds.aimConstraint(loc, cam, aimVector=(0,0,-1), upVector=(0,1,0),
                               worldUpType="vector", worldUpVector=(0,1,0))
        m = cmds.xform(cam, q=True, ws=True, m=True)
        cmds.delete(c); cmds.delete(loc)
        cmds.xform(cam, ws=True, m=m)
        try: cmds.setAttr(cam+".nearClipPlane", 5.0); cmds.setAttr(cam+".farClipPlane", 2200.0)
        except Exception: pass
        cmds.parent(cam, grp)
        if s["eye0"] != s["eye1"]:
            cmds.setKeyframe(cam, attribute="translateX", time=s["start"], value=s["eye0"][0])
            cmds.setKeyframe(cam, attribute="translateZ", time=s["start"], value=s["eye0"][2])
            cmds.setKeyframe(cam, attribute="translateX", time=s["end"], value=s["eye1"][0])
            cmds.setKeyframe(cam, attribute="translateZ", time=s["end"], value=s["eye1"][2])
    OUT["cams"] = len(cmap)
    json.dump(cmap, open(os.path.join(ROOT,"logs","cam_map_new.json"),"w",encoding="utf-8"), indent=1)
    cmds.file(os.path.join(ROOT,"scenes","手工摆位_v10.mb"), f=True, type="mayaBinary", ea=True)
    dump()
    shoot("S001", cmap["S001"], 30)
    shoot("S002", cmap["S002"], 80)
    shoot("S045", cmap["S045"], 2340)
    shoot("front", "OV_front1", 1)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
