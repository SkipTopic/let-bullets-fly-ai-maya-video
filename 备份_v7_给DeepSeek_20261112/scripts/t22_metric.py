import bpy, os, json, math
from mathutils import Vector

BASE = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
LOG = os.path.join(BASE, "logs", "bend_metric.json")

TESTS = [
    ("OLD_Ma", os.path.join(BASE, "models_fbx2", "CH_Ma.fbx")),
    ("NEW_Male", os.path.join(BASE, "models_new", "NH_MaleM_140", "Model", "NH_MaleM_140.fbx")),
]

rep = {}

for tag, path in TESTS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not os.path.exists(path):
        rep[tag] = {"error": "missing"}
        continue
    try:
        bpy.ops.import_scene.fbx(filepath=path)
    except Exception as e:
        rep[tag] = {"error": repr(e)}
        continue

    arm = next((o for o in bpy.context.scene.objects if o.type == 'ARMATURE'), None)
    mesh = next((o for o in bpy.context.scene.objects if o.type == 'MESH'), None)
    if not arm or not mesh:
        rep[tag] = {"error": "no armature/mesh"}
        continue

    names = [b.name for b in arm.data.bones]

    def find(keys):
        for k in keys:
            for n in names:
                if k.lower() == n.lower():
                    return n
        for k in keys:
            for n in names:
                if k.lower() in n.lower():
                    return n
        return None

    upper = find(["Bip001LUpperArm", "LUpperArm", "UpperArm_L", "upperarm_l", "LeftArm", "腕.L"])
    fore = find(["Bip001LForearm", "LForearm", "LowerArm_L", "lowerarm_l", "LeftForeArm", "ひじ.L"])
    rep[tag] = {"upper": upper, "fore": fore, "bones": len(names)}

    if not upper or not fore:
        rep[tag]["error"] = "arm bones not found"
        continue

    # 记录静止边长
    dg = bpy.context.evaluated_depsgraph_get()
    me = mesh.evaluated_get(dg).to_mesh()
    rest = [(me.vertices[e.vertices[0]].co - me.vertices[e.vertices[1]].co).length
            for e in me.edges]
    mesh.evaluated_get(dg).to_mesh_clear()

    # 弯手肘 95°
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    pb_f = arm.pose.bones[fore]
    pb_u = arm.pose.bones[upper]
    pb_f.rotation_mode = 'XYZ'
    pb_u.rotation_mode = 'XYZ'
    pb_u.rotation_euler = (0, 0, math.radians(-70))
    pb_f.rotation_euler = (math.radians(-95), 0, 0)
    bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()

    dg = bpy.context.evaluated_depsgraph_get()
    me2 = mesh.evaluated_get(dg).to_mesh()
    now = [(me2.vertices[e.vertices[0]].co - me2.vertices[e.vertices[1]].co).length
           for e in me2.edges]
    mesh.evaluated_get(dg).to_mesh_clear()

    ratios = []
    for r, n in zip(rest, now):
        if r > 1e-6:
            ratios.append(n / r)
    ratios.sort()
    cnt = len(ratios)
    rep[tag].update({
        "edges": cnt,
        "max_stretch": round(ratios[-1], 2),
        "p99": round(ratios[int(cnt * 0.99)], 2),
        "p95": round(ratios[int(cnt * 0.95)], 2),
        "over_1_8": round(sum(1 for x in ratios if x > 1.8) / cnt * 100, 2),
        "under_0_4": round(sum(1 for x in ratios if x < 0.4) / cnt * 100, 2),
    })

json.dump(rep, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE")
