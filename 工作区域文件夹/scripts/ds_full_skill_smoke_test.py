import os
import sys

SKILL_SCRIPTS = r"C:\Users\admin\Desktop\MayaProject\全流程 Skill\maya-sheng-animation\scripts"
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

from inspect_maya_project import inspect_project
from test_maya_camera_tools import run_test

root = os.path.dirname(SKILL_SCRIPTS)
inspection = os.path.join(root, "tests", "scene_inspection_smoke.json")
inspect_project(joints=[], output_path=inspection)
report = run_test(
    output_path=os.path.join(root, "tests", "maya_camera_test.json"),
    frames_dir=os.path.join(root, "tests", "camera_frames"),
)
if not report.get("ok"):
    raise RuntimeError("Full-flow camera smoke test failed: %r" % report)
