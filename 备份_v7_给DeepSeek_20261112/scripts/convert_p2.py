# -*- coding: utf-8 -*-
"""P2: convert PMX -> standardized FBX via Blender mmd_tools.

Usage: blender --background --python convert_p2.py -- <out.json> <pmx1> <out1.fbx> [<pmx2> <out2.fbx> ...]
Bone names standardized to English; shape keys renamed (mouth keys kept but will be zero-locked in Maya).
"""
import bpy
import sys
import json
import math
import traceback

ARGS = sys.argv[sys.argv.index('--') + 1:]
OUT_JSON = ARGS[0]
PAIRS = [(ARGS[i], ARGS[i + 1]) for i in range(1, len(ARGS), 2)]

BONE_MAP = {
    '全ての親': 'Root', 'センター': 'Center', 'グルーブ': 'Groove', '腰': 'Hips',
    '下半身': 'LowerBody', '上半身': 'Spine', '上半身2': 'Spine1',
    '首': 'Neck', '頭': 'Head', '両目': 'Eyes',
    '目.L': 'LeftEye', '目.R': 'RightEye',
    '肩.L': 'LeftShoulder', '肩.R': 'RightShoulder',
    '腕.L': 'LeftArm', '腕.R': 'RightArm',
    '腕捻.L': 'LeftArmTwist', '腕捻.R': 'RightArmTwist',
    'ひじ.L': 'LeftForeArm', 'ひじ.R': 'RightForeArm',
    '手捻.L': 'LeftForeArmTwist', '手捻.R': 'RightForeArmTwist',
    '手首.L': 'LeftHand', '手首.R': 'RightHand',
    '足.L': 'LeftUpLeg', '足.R': 'RightUpLeg',
    '足D.L': 'LeftUpLegRoll', '足D.R': 'RightUpLegRoll',
    'ひざ.L': 'LeftLeg', 'ひざ.R': 'RightLeg',
    'ひざD.L': 'LeftLegRoll', 'ひざD.R': 'RightLegRoll',
    '足首.L': 'LeftFoot', '足首.R': 'RightFoot',
    'つま先.L': 'LeftToeBase', 'つま先.R': 'RightToeBase',
    '親指０.L': 'LeftHandThumb1', '親指１.L': 'LeftHandThumb2', '親指２.L': 'LeftHandThumb3',
    '親指０.R': 'RightHandThumb1', '親指１.R': 'RightHandThumb2', '親指２.R': 'RightHandThumb3',
    '人指１.L': 'LeftHandIndex1', '人指２.L': 'LeftHandIndex2', '人指３.L': 'LeftHandIndex3',
    '人指１.R': 'RightHandIndex1', '人指２.R': 'RightHandIndex2', '人指３.R': 'RightHandIndex3',
    '中指１.L': 'LeftHandMiddle1', '中指２.L': 'LeftHandMiddle2', '中指３.L': 'LeftHandMiddle3',
    '中指１.R': 'RightHandMiddle1', '中指２.R': 'RightHandMiddle2', '中指３.R': 'RightHandMiddle3',
    '薬指１.L': 'LeftHandRing1', '薬指２.L': 'LeftHandRing2', '薬指３.L': 'LeftHandRing3',
    '薬指１.R': 'RightHandRing1', '薬指２.R': 'RightHandRing2', '薬指３.R': 'RightHandRing3',
    '小指１.L': 'LeftHandPinky1', '小指２.L': 'LeftHandPinky2', '小指３.L': 'LeftHandPinky3',
    '小指１.R': 'RightHandPinky1', '小指２.R': 'RightHandPinky2', '小指３.R': 'RightHandPinky3',
}

SK_MAP = {
    'まばたき': 'blink', 'ウィンク': 'wink_L', 'ウィンク右': 'wink_R', 'ウィンク２': 'wink2_L',
    'ｳｨﾝｸ２右': 'wink2_R',
    'あ': 'mouth_A', 'い': 'mouth_I', 'う': 'mouth_U', 'え': 'mouth_E', 'お': 'mouth_O', 'ん': 'mouth_N',
    'にやり': 'smile', 'にこり': 'smile2', 'なごみ': 'gentle', 'びっくり': 'surprise', '笑い': 'laugh',
    '困る': 'trouble', '怒り': 'anger', '真面目': 'serious', 'じと目': 'half_eye', '上': 'eye_up',
    '下': 'eye_down', '瞳小': 'pupil_small', '口横広げ': 'mouth_wide', '口角上げ': 'mouth_corner_up',
    '口角下げ': 'mouth_corner_down', 'ｷﾘｯ': 'keen',
}

report = {'models': {}}

for pmx, fbx_out in PAIRS:
    key = pmx.replace('\\', '/').split('/')[-1].replace('.pmx', '')
    ent = {}
    try:
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.ops.preferences.addon_enable(module='bl_ext.blender_org.mmd_tools')
        try:
            bpy.ops.preferences.addon_disable(module='bl_ext.blender_org.right_mouse_navigation')
        except Exception:
            pass
        bpy.ops.mmd_tools.import_model(filepath=pmx, scale=0.08,
                                       types={'MESH', 'ARMATURE', 'MORPHS'},
                                       clean_model=False, log_level='ERROR')
        arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
        meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        arm = arms[0]
        # rename bones
        bones = arm.data.bones
        nren = 0
        for b in list(bones):
            if b.name in BONE_MAP:
                b.name = BONE_MAP[b.name] + '_RNM'
        for b in list(bones):
            if b.name.endswith('_RNM'):
                b.name = b.name[:-4]
                nren += 1
        ent['bones_renamed'] = nren
        # rename shape keys
        skren = []
        for m in meshes:
            if m.data.shape_keys:
                for kb in m.data.shape_keys.key_blocks:
                    if kb.name in SK_MAP:
                        old = kb.name
                        kb.name = SK_MAP[old]
                        skren.append((old, kb.name))
        ent['sk_renamed'] = len(skren)
        # measure height (A-pose approx from bounding box)
        import mathutils
        mn = mathutils.Vector((1e9,) * 3)
        mx = mathutils.Vector((-1e9,) * 3)
        for o in meshes:
            for c in o.bound_box:
                wc = o.matrix_world @ mathutils.Vector(c)
                mn = mathutils.Vector(map(min, mn, wc))
                mx = mathutils.Vector(map(max, mx, wc))
        ent['height_m'] = round(mx.z - mn.z, 3)
        ent['n_verts'] = sum(len(m.data.vertices) for m in meshes)
        # export FBX
        bpy.ops.object.select_all(action='DESELECT')
        for o in bpy.context.scene.objects:
            if o.type in ('ARMATURE', 'MESH'):
                o.select_set(True)
        bpy.ops.export_scene.fbx(
            filepath=fbx_out, use_selection=True,
            object_types={'ARMATURE', 'MESH'}, add_leaf_bones=False,
            bake_anim=False, mesh_smooth_type='OFF',
            apply_unit_scale=True, global_scale=1.0,
            axis_forward='-Z', axis_up='Y')
        ent['ok'] = True
    except Exception:
        ent['ok'] = False
        ent['error'] = traceback.format_exc()
    report['models'][key] = ent

with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print('CONVERT_DONE')
