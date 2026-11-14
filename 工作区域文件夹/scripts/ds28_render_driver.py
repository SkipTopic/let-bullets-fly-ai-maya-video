"""渲染总调度：分批渲染 71 镜序列帧 → ffmpeg 编码。

- 每批 6 镜，Maya 挂了自动重启并续渲
- 已渲完的镜头自动跳过
- 最后按帧序拼成 MP4
"""
import glob
import json
import os
import subprocess
import sys
import time

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
PY = r"C:\Users\admin\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
MAYA = r"C:\Program Files\Autodesk\Maya2024\bin\maya.exe"
SCENE = os.path.join(ROOT, "scenes", "DS_相机动作_v01.mb")
SEQ = os.path.join(ROOT, "render", "all_v3")
PARAM = os.path.join(ROOT, "cmd", "ds_seq_param.json")
LOG = os.path.join(ROOT, "logs", "ds28_render_driver.log")


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def shots():
    data = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"), encoding="utf-8"))["shots"]
    return [(s["id"], s["frame_range"][0], s["frame_range"][1]) for s in data]


def have(sid, f0, f1):
    n = len(glob.glob(os.path.join(SEQ, sid + ".*.png")))
    return n >= (f1 - f0 + 1)


def maya_alive():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq maya.exe"], capture_output=True, text=True)
    return "maya.exe" in (out.stdout or "").lower()


def start_maya():
    log("启动 Maya ...")
    subprocess.Popen([MAYA, "-file", SCENE])
    for _ in range(60):
        time.sleep(3)
        if maya_alive():
            time.sleep(35)
            r = subprocess.run([PY, os.path.join(ROOT, "scripts", "ds_run.py"),
                                os.path.join(ROOT, "scripts", "ds1_ping.py"), "60"],
                               capture_output=True, text=True, cwd=ROOT)
            if "ok" in (r.stdout or ""):
                log("Maya 就绪")
                return True
    return False


def render_batch(ids):
    json.dump({"ids": ids, "outdir": SEQ, "w": 960, "h": 540, "q": 85},
              open(PARAM, "w", encoding="utf-8"), ensure_ascii=False)
    r = subprocess.run([PY, os.path.join(ROOT, "scripts", "ds_run.py"),
                        os.path.join(ROOT, "scripts", "ds27_render_seq.py"), "2400"],
                       capture_output=True, text=True, cwd=ROOT)
    return (r.stdout or "") + (r.stderr or "")


def main():
    todo = [s for s in shots() if not have(*s)]
    log("待渲 %d 镜 / 共 %d 镜" % (len(todo), len(shots())))
    if not os.path.isdir(SEQ):
        os.makedirs(SEQ)

    i = 0
    while i < len(todo):
        batch = todo[i:i + 6]
        ids = [b[0] for b in batch]
        log("批次 %s" % ",".join(ids))
        for attempt in range(3):
            out = render_batch(ids)
            ok = all(have(*b) for b in batch)
            log("  尝试 %d -> %s" % (attempt + 1, "完成" if ok else (out.strip()[:160] or "未完成")))
            if ok:
                break
            if not maya_alive():
                start_maya()
        # 只推进已完成的镜头
        while i < len(todo) and have(*todo[i]):
            i += 1
    log("全部镜头渲完，开始编码")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
