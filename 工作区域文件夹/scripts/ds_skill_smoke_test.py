import os
import sys

SKILL_SCRIPTS = r"C:\Users\admin\Desktop\MayaProject\解决人物模型的 Skill\maya-character-pose-recovery\scripts"
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

from test_maya_pose_tools import run_test

output = os.path.join(os.path.dirname(SKILL_SCRIPTS), "tests", "maya_two_bone_test.json")
report = run_test(output_path=output)
if not report.get("ok"):
    raise RuntimeError("Skill smoke test failed: %r" % report)
