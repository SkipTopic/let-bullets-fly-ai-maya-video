import os, json, hashlib, shutil
from datetime import datetime

PROJECT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试"
WORK = os.path.join(PROJECT, "工作区域文件夹")
BACKUP = os.path.join(PROJECT, "备份_v7_给DeepSeek_20261112")

if os.path.exists(BACKUP):
    raise SystemExit("Backup already exists; refusing to overwrite: " + BACKUP)
os.makedirs(BACKUP)

entries = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(4 * 1024 * 1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def copy_one(src, relative, category, note=""):
    if not os.path.isfile(src):
        raise FileNotFoundError(src)
    dst = os.path.join(BACKUP, relative)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    src_hash = sha256(src)
    dst_hash = sha256(dst)
    if src_hash != dst_hash:
        raise RuntimeError("SHA-256 mismatch: " + src)
    entries.append({
        "source": src,
        "backup": relative.replace("\\", "/"),
        "category": category,
        "note": note,
        "bytes": os.path.getsize(src),
        "sha256": src_hash,
        "copy_hash_matches": True,
    })


def copy_tree_files(src_dir, relative_dir, category, note=""):
    if not os.path.isdir(src_dir):
        raise FileNotFoundError(src_dir)
    for name in sorted(os.listdir(src_dir)):
        src = os.path.join(src_dir, name)
        if os.path.isfile(src):
            copy_one(src, os.path.join(relative_dir, name), category, note)


copy_one(os.path.join(PROJECT, "交接文档_给DeepSeek_摄像机与人物动作.md"), "交接文档_给DeepSeek_摄像机与人物动作.md", "handoff", "DeepSeek 首先阅读")
copy_one(os.path.join(PROJECT, "交接文档_给新对话.md"), "history/交接文档_给新对话.md", "history", "此前交接及 v7 追加记录")
copy_one(os.path.join(WORK, "scenes", "摆姿重建_v7.mb"), "scenes/摆姿重建_v7.mb", "scene", "唯一有效工作基线；先另存 DS 版本")
copy_one(os.path.join(WORK, "scenes", "NEWM_test.mb"), "scenes/NEWM_test.mb", "scene_reference", "清理过表情的新马县长；重建参考")
copy_one(os.path.join(WORK, "scenes", "手工摆位_v2.mb"), "scenes/手工摆位_v2.mb", "scene_history", "旧稳定基线；不要当作当前摆姿")
copy_one(os.path.join(WORK, "scenes", "v10_prod.mb"), "scenes/v10_prod.mb", "scene_history", "旧 v2 诊断证据；不要继续叠改")

for key in ("Ma", "Huang", "Shiye"):
    copy_one(os.path.join(WORK, "models_fbx2", "CH_%s.fbx" % key), "models_fbx2/CH_%s.fbx" % key, "model", "旧模型中立变换来源；马县长当前使用新模型")

for name in ("shotlist.csv", "shots.json", "camera_positions.csv"):
    note = "71 镜最高优先级文本依据" if name == "shotlist.csv" else "旧数据参考；机位不可直接复用"
    copy_one(os.path.join(WORK, name), "data/" + name, "shot_data", note)

copy_tree_files(os.path.join(WORK, "scripts"), "scripts", "scripts", "脚本含原项目绝对路径；移动后需改 ROOT")
copy_tree_files(os.path.join(WORK, "logs"), "logs", "logs", "执行和验收日志")
copy_tree_files(os.path.join(WORK, "_摆姿验收", "v7"), "validation/v7", "validation", "v7 四视图、16 张原图和回读数据")
copy_tree_files(os.path.join(WORK, "_独立复核"), "reference/independent_review", "reference_image")
copy_tree_files(os.path.join(WORK, "_摸底参考"), "reference/original_storyboard", "reference_image")
copy_tree_files(os.path.join(WORK, "subs"), "subtitles", "subtitles", "旧 480P 字幕 PNG；最终复用前核对")

for name in ("BN对比.png", "观察四视图2.png"):
    copy_one(os.path.join(WORK, "_审片", name), "reference/pose_history/" + name, "reference_image", "历史对照，不是当前验收图")

for name in ("DECISIONS.md", "进度.md", "00_自检报告.md", "验收评审_成片打分.md", "修复报告_p4_fixed.md"):
    copy_one(os.path.join(WORK, name), "history/" + name, "history", "历史结论需结合最新交接判断")
for name in ("依赖说明.md", "手工摆位说明.md"):
    copy_one(os.path.join(PROJECT, "交付_手动摆位", name), "history/old_delivery/" + name, "history", "旧交付说明；组 Y=0 等旧结论不适用于 v7")

copy_one(os.path.join(PROJECT, "原视频素材.mp4"), "reference/原视频素材.mp4", "reference_video", "原片画面和 AAC 音轨")
copy_one(os.path.join(PROJECT, "输出文件夹", "成片_鸿门宴复刻_480P_v2.mp4"), "reference/成片_鸿门宴复刻_480P_v2_旧版负面参考.mp4", "reference_video", "旧成片，仅作负面对照")

copy_one(r"C:\Users\admin\Documents\maya\2024\prefs\scripts\userSetup.py", "environment/userSetup.prefs.py", "environment", "原全局启动钩子参考副本")
copy_one(r"C:\Users\admin\Documents\maya\2024\zh_CN\prefs\scripts\userSetup.py", "environment/userSetup.zh_CN.py", "environment", "原中文启动钩子参考副本")

note_path = os.path.join(BACKUP, "先读_备份说明.txt")
note = """《让子弹飞》v7 -> DeepSeek 接续备份

1. 首先阅读根目录的《交接文档_给DeepSeek_摄像机与人物动作.md》。
2. 日常工作不要直接修改备份。复制 scenes/摆姿重建_v7.mb 到工作区并另存 DS_相机动作_v01.mb。
3. 本备份没有包含失败中间场景，旧 v10 和手工摆位_v2 仅为诊断/重建参考。
4. .mb 无外部 reference 和贴图依赖；脚本含原项目绝对路径，移动目录后需修改 ROOT/SCRIPTS。
5. manifest.json 记录源路径、相对路径、大小和 SHA-256；SHA256SUMS.txt 用于整体校验。
6. 备份只证明接续时点的文件状态，不代表新相机、人物动作或全片已经完成。
"""
with open(note_path, "w", encoding="utf-8") as fh:
    fh.write(note)
entries.append({"source": "generated", "backup": "先读_备份说明.txt", "category": "readme", "note": "备份使用说明", "bytes": os.path.getsize(note_path), "sha256": sha256(note_path), "copy_hash_matches": True})

manifest = {
    "backup_name": os.path.basename(BACKUP),
    "created_at": datetime.now().astimezone().isoformat(),
    "project": PROJECT,
    "primary_scene": "scenes/摆姿重建_v7.mb",
    "handoff": "交接文档_给DeepSeek_摄像机与人物动作.md",
    "file_count": len(entries),
    "total_bytes": sum(item["bytes"] for item in entries),
    "all_copy_hashes_match": all(item["copy_hash_matches"] for item in entries),
    "warnings": [
        "备份目录只读，不直接在其中制作动画或渲染。",
        "v7 是当前唯一有效基线；旧场景只作参考。",
        "下一阶段是 71 镜摄像机和头部/手部动作，尚未渲染新全片。",
        "脚本含原项目绝对路径，迁移后需要调整。",
    ],
    "files": entries,
}
with open(os.path.join(BACKUP, "manifest.json"), "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=1)
with open(os.path.join(BACKUP, "SHA256SUMS.txt"), "w", encoding="utf-8") as fh:
    for item in entries:
        fh.write("%s *%s\n" % (item["sha256"], item["backup"]))

print(json.dumps({"backup": BACKUP, "file_count": len(entries), "total_bytes": manifest["total_bytes"], "all_copy_hashes_match": manifest["all_copy_hashes_match"]}, ensure_ascii=False))
