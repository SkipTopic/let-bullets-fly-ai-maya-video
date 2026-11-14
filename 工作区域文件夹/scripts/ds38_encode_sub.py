"""拼帧 + 烧中文字幕成片。

用法：python ds38_encode_sub.py [src_dir] [out_mp4] [--test N]
"""
import glob
import json
import os
import shutil
import subprocess
import sys

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SRT = os.path.join(ROOT, "render", "subs_zh.srt")
LINK = os.path.join(ROOT, "render", "_seq_link2")

STYLE = ("FontName=Microsoft YaHei,FontSize=20,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,"
         "Alignment=2,MarginV=22")


def timeline(shots):
    out = []
    for s in shots:
        f0, f1 = s["frame_range"]
        for f in range(f0, f1 + 1):
            out.append((s["id"], f))
    return out


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "render", "all_v2")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "render", "让子弹飞_鸿门宴_DS_v02.mp4")
    test = 0
    if "--test" in sys.argv:
        test = int(sys.argv[sys.argv.index("--test") + 1])

    shots = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"),
                           encoding="utf-8"))["shots"]
    frames = timeline(shots)
    if test:
        frames = frames[:test]

    if os.path.isdir(LINK):
        shutil.rmtree(LINK)
    os.makedirs(LINK)
    missing = 0
    for i, (sid, f) in enumerate(frames, start=1):
        p = os.path.join(src, "%s.%04d.png" % (sid, f))
        d = os.path.join(LINK, "%05d.png" % i)
        if not os.path.exists(p):
            missing += 1
            continue
        try:
            os.link(p, d)
        except Exception:
            shutil.copyfile(p, d)
    print("frames", len(frames), "missing", missing)
    if missing:
        return 2

    sub = SRT.replace("\\", "/").replace(":", "\\:")
    vf = "subtitles='%s':force_style='%s'" % (sub, STYLE)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "24000/1001",
           "-start_number", "1", "-i", os.path.join(LINK, "%05d.png"),
           "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("subtitles failed, retry without:", r.stderr[-400:])
        cmd = [c for c in cmd if c != vf]
        r = subprocess.run(cmd, capture_output=True, text=True)
    print("rc", r.returncode, r.stderr[-300:] if r.returncode else "")
    if os.path.exists(out):
        print("out", out, round(os.path.getsize(out) / 1e6, 2), "MB")
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
