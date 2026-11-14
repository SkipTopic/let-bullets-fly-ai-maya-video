"""动画基础库：头看向目标、两骨 IK 放手、打关键帧。

在 Maya 内运行。设计原则：只动头/颈/上臂/前臂/手，不动躯干和腿，避免破坏 v7 坐姿。
"""
import math

import maya.cmds as cmds

HEAD = {"Ma": (0.02, 113.05, -105.24), "Huang": (90.39, 123.19, 51.87), "Shiye": (-89.20, 123.49, 51.37)}
SPINE = {"Ma": (0.0, 100.4, -105.2), "Huang": (88.1, 111.4, 50.0), "Shiye": (-88.1, 111.5, 50.0)}
YAW = {"Ma": 0.0, "Huang": -120.0, "Shiye": 120.0}

ARM = {
    "Ma": {
        "L": ("Bip001LUpperArm", "Bip001LForearm", "Bip001LHand"),
        "R": ("Bip001RUpperArm", "Bip001RForearm", "Bip001RHand"),
        "head": ("Bip001Head", "Bip001Neck"),
    },
    "Huang": {
        "L": ("Huang_LeftArm", "Huang_LeftForeArm", "Huang_LeftHand"),
        "R": ("Huang_RightArm", "Huang_RightForeArm", "Huang_RightHand"),
        "head": ("Huang_Head", "Huang_Neck"),
    },
    "Shiye": {
        "L": ("Shiye_LeftArm", "Shiye_LeftForeArm", "Shiye_LeftHand"),
        "R": ("Shiye_RightArm", "Shiye_RightForeArm", "Shiye_RightHand"),
        "head": ("Shiye_Head", "Shiye_Neck"),
    },
}


def fwd(name):
    y = math.radians(YAW[name])
    return (math.sin(y), 0.0, math.cos(y))


def left(name):
    f = fwd(name)
    return (f[2], 0.0, -f[0])


def pos(node):
    return tuple(cmds.xform(node, q=True, ws=True, t=True))


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    n = math.sqrt(dot(a, a)) or 1e-9
    return (a[0] / n, a[1] / n, a[2] / n)


def rot_axis_angle(axis, deg):
    """返回 3x3 旋转（行向量约定：p' = p * R）。"""
    x, y, z = norm(axis)
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    C = 1 - c
    return [
        [c + x * x * C, x * y * C + z * s, x * z * C - y * s],
        [y * x * C - z * s, c + y * y * C, y * z * C + x * s],
        [z * x * C + y * s, z * y * C - x * s, c + z * z * C],
    ]


def mat_apply(R, v):
    return (v[0] * R[0][0] + v[1] * R[1][0] + v[2] * R[2][0],
            v[0] * R[0][1] + v[1] * R[1][1] + v[2] * R[2][1],
            v[0] * R[0][2] + v[1] * R[1][2] + v[2] * R[2][2])


def rotate_about(node, pivot, R):
    """把节点绕 pivot 施加世界旋转 R（行向量约定）。"""
    m = cmds.xform(node, q=True, ws=True, m=True)
    # 取行列式保护，避免负缩放网格
    M = [[m[0], m[1], m[2]], [m[4], m[5], m[6]], [m[8], m[9], m[10]]]
    t = (m[12], m[13], m[14])
    # new_t = (t - pivot) * R + pivot
    d = sub(t, pivot)
    nd = mat_apply(R, d)
    nt = add(nd, pivot)
    # new_basis = M * R
    NM = [[sum(M[i][k] * R[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    flat = [NM[0][0], NM[0][1], NM[0][2], 0.0,
            NM[1][0], NM[1][1], NM[1][2], 0.0,
            NM[2][0], NM[2][1], NM[2][2], 0.0,
            nt[0], nt[1], nt[2], 1.0]
    cmds.xform(node, ws=True, m=flat)


def aim_head(name, target, yaw_limit=42.0, pitch_limit=26.0, neck_share=0.35):
    """让头部朝向 target：头骨转主要角度，脖子分担一部分。"""
    head_j, neck_j = ARM[name]["head"]
    hp = pos(head_j)
    d = sub(target, hp)
    want = norm((d[0], 0.0, d[2]))
    f = fwd(name)
    # 水平夹角
    cosy = max(-1.0, min(1.0, dot(f, want)))
    yaw = math.degrees(math.acos(cosy))
    if yaw > 1e-4:
        axis = cross(f, want)
        if math.sqrt(dot(axis, axis)) < 1e-6:
            axis = (0.0, 1.0, 0.0)
        sgn = 1.0 if dot(axis, (0.0, 1.0, 0.0)) >= 0 else -1.0
        yaw_signed = sgn * yaw
    else:
        yaw_signed = 0.0
    yaw_signed = max(-yaw_limit, min(yaw_limit, yaw_signed))

    # 俯仰
    horiz = math.sqrt(d[0] ** 2 + d[2] ** 2) or 1e-6
    pitch = math.degrees(math.atan2(d[1], horiz))
    pitch = max(-pitch_limit, min(pitch_limit, pitch))

    for j, share in ((neck_j, neck_share), (head_j, 1.0 - neck_share)):
        if share <= 0:
            continue
        p = pos(j)
        R1 = rot_axis_angle((0.0, 1.0, 0.0), yaw_signed * share)
        rotate_about(j, p, R1)
        if abs(pitch) > 1e-4:
            R2 = rot_axis_angle((1.0, 0.0, 0.0), -pitch * share)
            rotate_about(j, pos(j), R2)


def two_bone_ik(name, side, target, pole_dir=None):
    """把手指到 target：上臂 + 前臂两骨解析 IK。"""
    up_j, fore_j, hand_j = ARM[name][side]
    S = pos(up_j)
    E = pos(fore_j)
    W = pos(hand_j)
    L1 = math.dist(S, E)
    L2 = math.dist(E, W)
    d = sub(target, S)
    dist = math.sqrt(dot(d, d))
    dist = max(abs(L1 - L2) + 1.5, min(L1 + L2 - 1.5, dist))
    u = norm(d)

    # 肘部极向量：默认用手当前肘部相对肩-手连线的垂直分量
    if pole_dir is None:
        v = sub(E, S)
        proj = mul(u, dot(v, u))
        pole = sub(v, proj)
        if math.sqrt(dot(pole, pole)) < 1e-4:
            pole = cross(u, (0.0, 1.0, 0.0))
    else:
        pole = pole_dir
    pole = norm(pole)
    # 肘部在圆周上的方向
    cos_a = (L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist)
    cos_a = max(-1.0, min(1.0, cos_a))
    a = math.acos(cos_a)
    # E' = S + u*L1*cos(a) + pole*L1*sin(a)
    Ep = add(add(S, mul(u, L1 * math.cos(a))), mul(pole, L1 * math.sin(a)))

    # 1) 转上臂，使 (E-S) -> (E'-S)
    v1 = norm(sub(E, S))
    v2 = norm(sub(Ep, S))
    ax = cross(v1, v2)
    if math.sqrt(dot(ax, ax)) > 1e-6:
        ang = math.degrees(math.acos(max(-1.0, min(1.0, dot(v1, v2)))))
        rotate_about(up_j, S, rot_axis_angle(ax, ang))

    # 2) 转前臂，使手腕到目标
    E2 = pos(fore_j)
    W2 = pos(hand_j)
    w1 = norm(sub(W2, E2))
    w2 = norm(sub(target, E2))
    ax2 = cross(w1, w2)
    if math.sqrt(dot(ax2, ax2)) > 1e-6:
        ang2 = math.degrees(math.acos(max(-1.0, min(1.0, dot(w1, w2)))))
        rotate_about(fore_j, E2, rot_axis_angle(ax2, ang2))
    return pos(hand_j)


def snapshot(joints):
    snap = {}
    for j in joints:
        snap[j] = (list(cmds.xform(j, q=True, ro=True)), list(cmds.xform(j, q=True, t=True)))
    return snap


def restore(snap):
    for j, (ro, t) in snap.items():
        cmds.xform(j, ro=ro)
        cmds.xform(j, t=t)


def key_joints(joints, frame):
    for j in joints:
        cmds.setKeyframe(j, at="rotate", time=frame)
        cmds.setKeyframe(j, at="translate", time=frame)
