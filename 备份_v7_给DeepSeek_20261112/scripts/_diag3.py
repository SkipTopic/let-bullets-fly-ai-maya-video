import maya.cmds as cmds, json, os
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
out = {}
for side in ("Left", "Right"):
    n = "Ma_%sHand" % side
    ch = []
    cur = n
    while cur and len(ch) < 12:
        ch.append(cur)
        p = cmds.listRelatives(cur, parent=True)
        cur = p[0] if p else None
    out[side] = ch
out["right_forearm_exists"] = bool(cmds.objExists("Ma_RightForeArm"))
out["right_arm_rot_order"] = cmds.getAttr("Ma_RightArm.rotateOrder")
out["left_arm_rot_order"] = cmds.getAttr("Ma_LeftArm.rotateOrder")
out["right_arm_joint_orient"] = [round(v,2) for v in cmds.getAttr("Ma_RightArm.jointOrient")[0]]
out["left_arm_joint_orient"] = [round(v,2) for v in cmds.getAttr("Ma_LeftArm.jointOrient")[0]]
json.dump(out, open(os.path.join(ROOT,"logs","_diag3.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
