import bpy, os, json, math
from mathutils import Vector

BASE = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = os.path.join(BASE, "_审片")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(BASE, "logs", "bend_test.json")

TESTS = [
    ("NEW_Male", os.path.join(BASE, "models_new", "NH_MaleM_140", "Model", "NH_MaleM_140.fbx")),
    ("OLD_Ma", os.path.join(BASE, "models_fbx2", "CH_Ma.fbx")),
]

rep = {}

for tag, path in TESTS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not os.path.exists(path):
        rep[tag] = {"error": "missing"}
        continue
    bpy.ops.import_scene.fbx(filepath=path)

    arm = next((o for o in bpy.context.scene.objects if o.type == 'ARMATURE'), None)
    if not arm:
        rep[tag] = {"error": "no armature"}
        continue

    names = [b.name for b in arm.data.bones]
    # 找上臂/前臂
    def find(keys):
        for k in keys:
            for n in names:
                if k.lower() in n.lower():
                    return n
        return None

    upper = find(["LUpperArm", "UpperArm_L", "upperarm_l", "LeftArm", "腕.L"])
    fore = find(["LForearm", "LowerArm_L", "lowerarm_l", "LeftForeArm", "ひじ.L"])
    rep[tag] = {"upper": upper, "fore": fore, "bones": len(names),
                "arm_bones": [n for n in names if "arm" in n.lower() or "腕" in n][:12]}

    if not upper or not fore:
        rep[tag]["error"] = "arm bones not found"
        continue

    # 弯手肘
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    pb_f = arm.pose.bones[fore]
    pb_u = arm.pose.bones[upper]
    pb_f.rotation_mode = 'XYZ'
    pb_u.rotation_mode = 'XYZ'
    # 上臂往下摆、前臂往里弯
    pb_u.rotation_euler = (0, 0, math.radians(-70))
    pb_f.rotation_euler = (math.radians(-95), 0, 0)
    bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='OBJECT')

    # 计算包围盒，架相机拍肩部
    mesh = next((o for o in bpy.context.scene.objects if o.type == 'MESH'), None)
    if mesh:
        mw = mesh.matrix_world
        bb = [mw @ Vector(c) for c in mesh.bound_box]
        zs = [v.z for v in bb]; xs = [v.x for v in bb]; ys = [v.y for v in bb]
        cz = (min(zs) + max(zs)) / 2
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        rep[tag]["bbox"] = [round(min(xs), 2), round(min(ys), 2), round(min(zs), 2),
                            round(max(xs), 2), round(max(ys), 2), round(max(zs), 2)]

        cam_data = bpy.data.cameras.new("C")
        cam_data.lens = 85
        cam = bpy.data.objects.new("C", cam_data)
        bpy.context.scene.collection.objects.link(cam)
        # 从正前方偏左拍上半身
        cam.location = (cx + 0.9, cy - 1.5, cz + 0.55)
        target = Vector((cx + 0.15, cy, cz + 0.35))
        direction = target - cam.location
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.camera = cam

        sc = bpy.context.scene
        sc.render.engine = 'BLENDER_WORKBENCH'
        sc.render.resolution_x = 800
        sc.render.resolution_y = 600
        sc.display.shading.light = 'STUDIO'
        sc.display.shading.color_type = 'SINGLE'
        sc.display.shading.single_color = (0.75, 0.75, 0.78)
        sc.render.filepath = os.path.join(OUT, "BEND_%s.png" % tag)
        bpy.ops.render.render(write_still=True)
        rep[tag]["png"] = sc.render.filepath

json.dump(rep, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE")
