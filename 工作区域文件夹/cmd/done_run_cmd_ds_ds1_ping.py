"""DS ping：确认 Maya 轮询通道、当前场景、单位和播放范围。"""
import json
import os

import maya.cmds as cmds

OUT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\logs"
os.makedirs(OUT, exist_ok=True)

d = {
    "ok": True,
    "maya": cmds.about(version=True),
    "scene": cmds.file(q=True, sn=True),
    "time_unit": cmds.currentUnit(q=True, time=True),
    "linear_unit": cmds.currentUnit(q=True, linear=True),
    "fps": cmds.currentUnit(q=True, time=True),
    "playback": [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)],
    "frames_per_sec_check": cmds.playbackOptions(q=True, fps=True),
    "modified": cmds.file(q=True, modified=True),
}

with open(os.path.join(OUT, "ds1_ping.json"), "w", encoding="utf-8") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
print(json.dumps(d, ensure_ascii=False))
