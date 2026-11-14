import maya.cmds as cmds
import maya.api.OpenMaya as om
import json, os, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SCENE = os.path.join(ROOT, "scenes", "摆姿重建_v1.mb")
REST = json.load(open(os.path.join(ROOT, "logs", "q2_rest.json"), encoding="utf-8"))
OUT = {"errors": [], "characters": {}, "restore_failures": []}
SEAT_HIP_Y = 54.0
TABLE_TOP = 75.75

OLD = {
    "Huang": {
        "group": "CHR_Huang", "prefix": "Huang_", "mesh": "Huang_AragakiFBXASC032Shinjiro_mesh",
        "hip_l": "Huang_LeftUpLeg", "hip_r": "Huang_RightUpLeg",
        "legs": (("Left", "Huang_LeftUpLeg", "Huang_LeftLeg", "Huang_LeftFoot"), ("Right", "Huang_RightUpLeg", "Huang_RightLeg", "Huang_RightFoot")),
        "arms": (("Left", "Huang_LeftArm", "Huang_LeftHand"), ("Right", "Huang_RightArm", "Huang_RightHand")),
        "spine": "Huang_Spine", "head": "Huang_Head", "seat": 1,
    },
    "Shiye": {
        "group": "CHR_Shiye", "prefix": "Shiye_", "mesh": "Shiye_JunpeiFBXASC032Iori_mesh",
        "hip_l": "Shiye_LeftUpLeg", "hip_r": "Shiye_RightUpLeg",
        "legs": (("Left", "Shiye_LeftUpLeg", "Shiye_LeftLeg", "Shiye_LeftFoot"), ("Right", "Shiye_RightUpLeg", "Shiye_RightLeg", "Shiye_RightFoot")),
        "arms": (("Left", "Shiye_LeftArm", "Shiye_LeftHand"), ("Right", "Shiye_RightArm", "Shiye_RightHand")),
        "spine": "Shiye_Spine", "head": "Shiye_Head", "seat": 2,
    },
}


def vadd(a, b):
    return [a[i] + b[i] for i in range(3)]


def vmul(a, s):
    return [a[i] * s for i in range(3)]


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def pos(node):
    return list(cmds.xform(node, q=True, ws=True, t=True))


def directions(group):
    yaw = math.radians(cmds.getAttr(group + ".rotateY"))
    return [math.sin(yaw), 0.0, math.cos(yaw)], [math.cos(yaw), 0.0, -math.sin(yaw)]


def set_vector(node, attr, value):
    try:
        cmds.setAttr(node + "." + attr, *value)
        return True
    except Exception:
        OUT["restore_failures"].append(node + "." + attr)
        return False


def restore_old(key):
    prefix = key + "_"
    for name, data in REST["characters"][key]["transforms"].items():
        target = prefix + name
        if not cmds.objExists(target):
            continue
        for attr in ("translate", "rotate", "scale", "jointOrient"):
            if attr in data and cmds.attributeQuery(attr, node=target, exists=True):
                set_vector(target, attr, data[attr])
    cmds.refresh(force=True)


def bake_ik(start, end, target, pole):
    handle = cmds.ikHandle(sj=start, ee=end, sol="ikRPsolver")[0]
    locator = cmds.spaceLocator(name="TMP_PV")[0]
    cmds.setAttr(locator + ".translate", *pole)
    cmds.poleVectorConstraint(locator, handle)
    cmds.move(target[0], target[1], target[2], handle, absolute=True, worldSpace=True)
    cmds.refresh(force=True)
    chain = []
    cur = end
    while cur:
        chain.append(cur)
        if cur == start:
            break
        parents = cmds.listRelatives(cur, parent=True)
        cur = parents[0] if parents else None
    if not chain or chain[-1] != start:
        raise RuntimeError("IK chain mismatch: %s -> %s" % (start, end))
    rotations = {bone: list(cmds.getAttr(bone + ".rotate")[0]) for bone in chain}
    got = pos(end)
    cmds.delete(handle)
    cmds.delete(locator)
    for bone, value in rotations.items():
        cmds.setAttr(bone + ".rotate", *value)
    cmds.refresh(force=True)
    return {"target": target, "got": got, "error": distance(target, got), "rotations": rotations}


def sit_legs(key, cfg):
    group = cfg["group"]
    fwd, right = directions(group)
    hip_positions = [pos(cfg["hip_l"]), pos(cfg["hip_r"])]
    hip_y = sum(p[1] for p in hip_positions) / 2.0
    group_y = cmds.getAttr(group + ".translateY")
    cmds.setAttr(group + ".translateY", group_y + SEAT_HIP_Y - hip_y)
    cmds.refresh(force=True)
    foot_neutral_rot = {foot: list(cmds.xform(foot, q=True, ws=True, ro=True)) for _side, _thigh, _calf, foot in cfg["legs"]}
    result = {"hip_target_y": SEAT_HIP_Y, "legs": {}}
    for side, thigh, calf, foot in cfg["legs"]:
        hip = pos(thigh)
        knee_rest = pos(calf)
        ankle_rest = pos(foot)
        thigh_len = distance(hip, knee_rest)
        calf_len = distance(knee_rest, ankle_rest)
        ground_ankle_y = cfg["ankle_ground"]
        target = vadd(hip, vmul(fwd, thigh_len * 0.96))
        target[1] = ground_ankle_y
        pole = vadd(hip, vmul(fwd, thigh_len * 1.8))
        pole[1] += 8.0
        solved = bake_ik(thigh, foot, target, pole)
        cmds.xform(foot, ws=True, ro=foot_neutral_rot[foot])
        cmds.refresh(force=True)
        solved.update({"thigh_length": thigh_len, "calf_length": calf_len, "hip": hip, "knee": pos(calf), "ankle_after": pos(foot)})
        result["legs"][side] = solved
    result["hip_after_y"] = (pos(cfg["hip_l"])[1] + pos(cfg["hip_r"])[1]) / 2.0
    return result


def drop_old_arms(key, cfg):
    fwd, right = directions(cfg["group"])
    result = {}
    for side, start, end in cfg["arms"]:
        sign = 1.0 if side == "Left" else -1.0
        shoulder = pos(start)
        elbow = pos(cfg["prefix"] + side + "ForeArm")
        wrist = pos(end)
        arm_len = distance(shoulder, elbow) + distance(elbow, wrist)
        target = vadd(shoulder, vmul(right, sign * 5.0))
        target = vadd(target, vmul(fwd, 3.0))
        target[1] = shoulder[1] - arm_len * 0.88
        pole = vadd(shoulder, vmul(right, sign * 15.0))
        pole = vadd(pole, vmul(fwd, -10.0))
        pole[1] -= 15.0
        solved = bake_ik(start, end, target, pole)
        result[side] = {"target": target, "got": pos(end), "error": solved["error"]}
    return result


def ma_hands_on_table(cfg):
    fwd, right = directions(cfg["group"])
    center = cmds.getAttr(cfg["group"] + ".translate")[0]
    result = {}
    for side, start, end in cfg["arms"]:
        sign = 1.0 if side == "Left" else -1.0
        shoulder = pos(start)
        target = vadd(center, vmul(right, sign * 18.0))
        target = vadd(target, vmul(fwd, 30.0))
        target[1] = TABLE_TOP + 6.0
        pole = vadd(shoulder, vmul(right, sign * 48.0))
        pole = vadd(pole, vmul(fwd, 10.0))
        pole[1] = TABLE_TOP - 12.0
        solved = bake_ik(start, end, target, pole)
        result[side] = {"target": target, "got": pos(end), "error": solved["error"], "shoulder": shoulder, "pole": pole}
    return result


def torso_metric(cfg):
    a = pos(cfg["spine"])
    b = pos(cfg["head"])
    dy = b[1] - a[1]
    horizontal = math.sqrt((b[0] - a[0]) ** 2 + (b[2] - a[2]) ** 2)
    angle = math.degrees(math.atan2(horizontal, max(dy, 0.001)))
    fwd, _right = directions(cfg["group"])
    signed_forward = (b[0] - a[0]) * fwd[0] + (b[2] - a[2]) * fwd[2]
    return {"spine": a, "head": b, "angle_from_up": angle, "signed_forward": signed_forward}


def mesh_metrics(cfg):
    mesh_tr = cfg["mesh"]
    shape = cmds.listRelatives(mesh_tr, shapes=True, ni=True, fullPath=True)[0]
    bbox = list(cmds.xform(mesh_tr, q=True, ws=True, bb=True))
    sel = om.MSelectionList()
    sel.add(shape)
    dag = sel.getDagPath(0)
    fn = om.MFnMesh(dag)
    points = fn.getPoints(om.MSpace.kWorld)
    table_count = 0
    chair_count = 0
    seat_bb = cmds.xform("SET_seat_%d" % cfg["seat"], q=True, ws=True, bb=True)
    for p in points:
        if 71.75 < p.y < 75.25 and p.x * p.x + p.z * p.z < 87.0 * 87.0:
            table_count += 1
        if seat_bb[0] + 1.0 < p.x < seat_bb[3] - 1.0 and seat_bb[2] + 1.0 < p.z < seat_bb[5] - 1.0 and seat_bb[1] + 0.5 < p.y < seat_bb[4] - 0.5:
            chair_count += 1
    return {
        "bbox": bbox,
        "size": [bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2]],
        "vertices": len(points),
        "table_interior_vertices": table_count,
        "chair_interior_vertices": chair_count,
        "hands": {side: pos(end) for side, _start, end in cfg["arms"]},
        "feet": {side: pos(foot) for side, _thigh, _calf, foot in cfg["legs"]},
    }


try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, f=True)
    cmds.currentTime(1)

    # This new pose-only scene intentionally omits the old shot cameras.
    for group in ("CAMERAS", "OBSERVATION_CAMERAS"):
        if cmds.objExists(group):
            cmds.delete(group)

    # Remove only the old Ma character; Huang and Shiye keep their meshes/materials.
    for node in ("CHR_Ma", "Ma_MakotoFBXASC032Yuki_mesh", "Ma_mmd_sdef_c", "Ma_mmd_sdef_r0", "Ma_mmd_sdef_r1"):
        if cmds.objExists(node):
            cmds.delete(node)

    # Restore original FBX local transforms, including the armature and mesh transforms.
    for key in OLD:
        restore_old(key)

    # Import the already stripped new Ma scene; never import the full morph FBX here.
    cmds.file(os.path.join(ROOT, "scenes", "NEWM_test.mb"), i=True, ignoreVersion=True, mergeNamespacesOnClash=False)
    ma_group = cmds.group(em=True, name="CHR_Ma")
    cmds.parent("Root", ma_group)
    cmds.parent(ma_group, "CHARS")
    cmds.setAttr(ma_group + ".translate", 0.0, 0.0, -102.0)
    cmds.setAttr(ma_group + ".rotate", 0.0, 0.0, 0.0)
    cmds.refresh(force=True)

    NEW = {
        "group": "CHR_Ma", "prefix": "Bip001", "mesh": "NH_MaleM_140_LOD0",
        "hip_l": "Bip001LThigh", "hip_r": "Bip001RThigh",
        "legs": (("Left", "Bip001LThigh", "Bip001LCalf", "Bip001LFoot"), ("Right", "Bip001RThigh", "Bip001RCalf", "Bip001RFoot")),
        "arms": (("Left", "Bip001LUpperArm", "Bip001LHand"), ("Right", "Bip001RUpperArm", "Bip001RHand")),
        "spine": "Bip001Spine", "head": "Bip001Head", "seat": 0,
        "ankle_ground": 10.1,
    }

    # Ground offset comes from each original neutral mesh and ankle height.
    for key, cfg in OLD.items():
        main = max(REST["characters"][key]["meshes"], key=lambda item: item["vertices"])
        foot_y = REST["characters"][key]["key_positions"]["LeftFoot"]["world"][1]
        cfg["ankle_ground"] = foot_y - main["bbox"][1] + 0.2

    for key, cfg in OLD.items():
        rec = {"restored_from": "models_fbx2/CH_%s.fbx" % key}
        rec["sit"] = sit_legs(key, cfg)
        rec["arms_down"] = drop_old_arms(key, cfg)
        rec["torso"] = torso_metric(cfg)
        rec["mesh"] = mesh_metrics(cfg)
        OUT["characters"][key] = rec

    rec = {"restored_from": "scenes/NEWM_test.mb", "mesh_parent_preserved": cmds.listRelatives(NEW["mesh"], parent=True) or []}
    rec["sit"] = sit_legs("Ma", NEW)
    rec["arms_table"] = ma_hands_on_table(NEW)
    rec["torso"] = torso_metric(NEW)
    rec["mesh"] = mesh_metrics(NEW)
    OUT["characters"]["Ma"] = rec

    cmds.currentTime(1)
    cmds.playbackOptions(min=1, max=3512, animationStartTime=1, animationEndTime=3512)
    cmds.select(clear=True)
    cmds.refresh(force=True)
    cmds.file(rename=SCENE)
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["saved"] = SCENE
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "q3_rebuild_pose.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
