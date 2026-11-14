import maya.cmds as cmds
import maya.api.OpenMaya as om
import json, os, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SCENE = os.path.join(ROOT, "scenes", "摆姿重建_v7.mb")
EXPECTED = json.load(open(os.path.join(ROOT, "logs", "q3_rebuild_pose_v7.json"), encoding="utf-8"))["characters"]
OUT = {"errors": [], "characters": {}}
CONFIG = {
    "Ma": {"mesh": "NH_MaleM_140_LOD0", "spine": "Bip001Spine", "head": "Bip001Head", "seat": 0, "legs": {"Left": "Bip001LFoot", "Right": "Bip001RFoot"}, "arms": {"Left": "Bip001LHand", "Right": "Bip001RHand"}},
    "Huang": {"mesh": "Huang_AragakiFBXASC032Shinjiro_mesh", "spine": "Huang_Spine", "head": "Huang_Head", "seat": 1, "legs": {"Left": "Huang_LeftFoot", "Right": "Huang_RightFoot"}, "arms": {"Left": "Huang_LeftHand", "Right": "Huang_RightHand"}},
    "Shiye": {"mesh": "Shiye_JunpeiFBXASC032Iori_mesh", "spine": "Shiye_Spine", "head": "Shiye_Head", "seat": 2, "legs": {"Left": "Shiye_LeftFoot", "Right": "Shiye_RightFoot"}, "arms": {"Left": "Shiye_LeftHand", "Right": "Shiye_RightHand"}},
}


def pos(node):
    return list(cmds.xform(node, q=True, ws=True, t=True))


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


try:
    cmds.file(SCENE, o=True, f=True)
    cmds.currentTime(1)
    cmds.refresh(force=True)
    OUT["scene"] = cmds.file(q=True, sn=True)
    OUT["review_camera_count"] = len([c for c in (cmds.ls(type="camera", long=True) or []) if "|POSE_REVIEW_CAMERAS|" in c])
    OUT["production_camera_count"] = len([c for c in (cmds.ls(type="camera", long=True) or []) if "|CAMERAS|" in c])
    OUT["delta_mush"] = cmds.ls(type="deltaMush") or []
    for key, cfg in CONFIG.items():
        mesh = cfg["mesh"]
        shape = cmds.listRelatives(mesh, shapes=True, ni=True, fullPath=True)[0]
        bbox = list(cmds.xform(mesh, q=True, ws=True, bb=True))
        spine = pos(cfg["spine"])
        head = pos(cfg["head"])
        horizontal = math.sqrt((head[0] - spine[0]) ** 2 + (head[2] - spine[2]) ** 2)
        angle = math.degrees(math.atan2(horizontal, max(head[1] - spine[1], 0.001)))
        sel = om.MSelectionList()
        sel.add(shape)
        fn = om.MFnMesh(sel.getDagPath(0))
        points = fn.getPoints(om.MSpace.kWorld)
        table_count = 0
        chair_count = 0
        seat = cmds.xform("SET_seat_%d" % cfg["seat"], q=True, ws=True, bb=True)
        for p in points:
            if 71.75 < p.y < 75.25 and p.x * p.x + p.z * p.z < 87.0 * 87.0:
                table_count += 1
            if seat[0] + 1.0 < p.x < seat[3] - 1.0 and seat[2] + 1.0 < p.z < seat[5] - 1.0 and seat[1] + 0.5 < p.y < seat[4] - 0.5:
                chair_count += 1
        expected = EXPECTED[key]
        leg_errors = {side: distance(pos(cfg["legs"][side]), expected["sit"]["legs"][side]["effective_target"]) for side in cfg["legs"]}
        arm_key = "arms_table" if key == "Ma" else "arms_down"
        arm_errors = {side: distance(pos(cfg["arms"][side]), expected[arm_key][side]["target"]) for side in cfg["arms"]}
        rec = {
            "visible": cmds.getAttr(mesh + ".visibility"),
            "mesh_parent": cmds.listRelatives(mesh, parent=True) or [],
            "torso_angle_from_up_degrees": angle,
            "bbox_size_cm": [bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2]],
            "lowest_vertex_y_cm": bbox[1],
            "table_interior_vertices": table_count,
            "chair_contact_vertices_for_visual_review": chair_count,
            "leg_target_errors_cm": leg_errors,
            "hand_target_errors_cm": arm_errors,
            "hand_positions_cm": {side: pos(cfg["arms"][side]) for side in cfg["arms"]},
            "foot_positions_cm": {side: pos(cfg["legs"][side]) for side in cfg["legs"]},
        }
        rec["hard_metrics_pass"] = bool(rec["visible"] and angle < 8.0 and table_count == 0 and bbox[1] > -0.5 and bbox[4] < 170.0 and max(leg_errors.values()) < 0.01 and max(arm_errors.values()) < 0.01)
        OUT["characters"][key] = rec
    OUT["all_hard_metrics_pass"] = all(rec["hard_metrics_pass"] for rec in OUT["characters"].values()) and OUT["review_camera_count"] == 16 and OUT["production_camera_count"] == 0 and not OUT["delta_mush"]
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

path = os.path.join(ROOT, "_摆姿验收", "v7", "验收数据.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
