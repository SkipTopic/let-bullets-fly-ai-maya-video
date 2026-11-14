"""把 71 镜序列帧按帧序拼成 MP4。"""
import glob
import json
import os
import subprocess
import sys

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SEQ = os.path.join(ROOT, "render", "all")
LINK = os.path.join(ROOT, "render", "_seq_link")
OUT = os.path.join(ROOT, "render", "让子弹飞_鸿门宴_DS_v01.mp4")


def timeline():
    shots = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"), encoding="utf-8"))["shots"]
    frames = []
    for s in shots:
        f0, f1 = s["frame_range"]
        for f in range(f0, f1 + 1):
            frames.append((s["id"], f))
    return frames


def main():
    frames = timeline()
    if os.path.isdir(LINK):
        for f in glob.glob(os.path.join(LINK, "*")):
            os.remove(f)
    else:
        os.makedirs(LINK)
    missing = []
    for i, (sid, f) in enumerate(frames, start=1):
        src = os.path.join(SEQ, "%s.%04d.png" % (sid, f))
        dst = os.path.join(LINK, "%05d.png" % i)
        if not os.path.exists(src):
            missing.append(src)
            continue
        try:
            os.link(src, dst)
        except Exception:
            import shutil
            shutil.copyfile(src, dst)
    print("frames", len(frames), "missing", len(missing))
    if missing:
        print("前 5 个缺失:", missing[:5])
        return 2

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-framerate", "24000/1001", "-start_number", "1",
           "-i", os.path.join(LINK, "%05d.png"),
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("ffmpeg rc", r.returncode, r.stderr[-800:] if r.returncode else "")
    if os.path.exists(OUT):
        print("output", OUT, round(os.path.getsize(OUT) / 1e6, 1), "MB")
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
