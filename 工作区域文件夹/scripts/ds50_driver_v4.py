"""v04 渲染调度：分批调用 ds48（离屏 + 黑帧记录），Maya 掉线重启续渲。"""
import glob, json, os, subprocess, time

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
PY = r"C:\Users\admin\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
MAYA = r"C:\Program Files\Autodesk\Maya2024\bin\maya.exe"
SCENE = os.path.join(ROOT, "scenes", "DS_相机动作_v01.mb")
SEQ = os.path.join(ROOT, "render", "all_v4")
PARAM = os.path.join(ROOT, "cmd", "ds_v4_param.json")
LOG = os.path.join(ROOT, "logs", "ds50_driver.log")


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def shots():
    data = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"), encoding="utf-8"))["shots"]
    return [(s["id"], s["frame_range"][0], s["frame_range"][1]) for s in data]


def have(sid, f0, f1):
    return len(glob.glob(os.path.join(SEQ, sid + ".*.png"))) >= (f1 - f0 + 1)


def maya_alive():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq maya.exe"], capture_output=True, text=True)
    return "maya.exe" in (out.stdout or "").lower()


def start_maya():
    log("启动 Maya ...")
    subprocess.Popen([MAYA, "-file", SCENE])
    for _ in range(60):
        time.sleep(3)
        if maya_alive():
            time.sleep(40)
            r = subprocess.run([PY, os.path.join(ROOT, "scripts", "ds_run.py"),
                                os.path.join(ROOT, "scripts", "ds1_ping.py"), "90"],
                               capture_output=True, text=True, cwd=ROOT)
            if "ok" in (r.stdout or ""):
                log("Maya 就绪")
                return True
    return False


def main():
    os.makedirs(SEQ, exist_ok=True)
    todo = [s for s in shots() if not have(*s)]
    log("待渲 %d 镜" % len(todo))
    i = 0
    while i < len(todo):
        batch = todo[i:i + 6]
        ids = [b[0] for b in batch]
        log("批次 %s" % ",".join(ids))
        for attempt in range(3):
            json.dump({"ids": ids, "outdir": SEQ, "w": 960, "h": 540, "q": 85},
                      open(PARAM, "w", encoding="utf-8"), ensure_ascii=False)
            r = subprocess.run([PY, os.path.join(ROOT, "scripts", "ds_run.py"),
                                os.path.join(ROOT, "scripts", "ds48_render_v4.py"), "2400"],
                               capture_output=True, text=True, cwd=ROOT)
            ok = all(have(*b) for b in batch)
            log("  尝试 %d -> %s" % (attempt + 1, "完成" if ok else (r.stdout or "")[:120]))
            if ok:
                break
            if not maya_alive():
                start_maya()
        while i < len(todo) and have(*todo[i]):
            i += 1
    log("渲染完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
