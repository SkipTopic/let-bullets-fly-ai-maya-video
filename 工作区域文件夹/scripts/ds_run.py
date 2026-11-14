"""DS 通用执行器：把 scripts 下的某个 .py 交给 Maya 轮询执行，并打印结果。

用法：
  python ds_run.py <脚本文件名或绝对路径> [timeout]
"""
import os
import sys
import time

sys.path.insert(0, r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts")
import mcmd  # noqa: E402

SCRIPTS = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts"


def main():
    if len(sys.argv) < 2:
        print("usage: ds_run.py <script> [timeout]")
        return 2
    target = sys.argv[1]
    if not os.path.isabs(target):
        target = os.path.join(SCRIPTS, target)
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    stem = os.path.splitext(os.path.basename(target))[0]
    # 每次跑用唯一 tag，避免读到上一轮残留的 result_run_*.json
    tag = "ds_%s_%s" % (stem, time.strftime("%H%M%S"))
    res = mcmd.run_file(target, timeout=timeout, tag=tag)
    print(res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
