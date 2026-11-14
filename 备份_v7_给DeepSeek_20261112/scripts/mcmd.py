"""把 Python 代码丢给 Maya 的文件轮询执行器，等待结果 JSON。"""
import os, time, uuid

CMD_DIR = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\cmd"


def run(code, timeout=1800, tag=None):
    os.makedirs(CMD_DIR, exist_ok=True)
    key = tag or uuid.uuid4().hex[:10]
    src = os.path.join(CMD_DIR, "cmd_%s.py" % key)
    res = os.path.join(CMD_DIR, "result_cmd_%s.json" % key)
    res2 = os.path.join(CMD_DIR, "result_run_cmd_%s.json" % key)
    if os.path.exists(res):
        os.remove(res)
    with open(src, "w", encoding="utf-8") as fh:
        fh.write(code)
    t0 = time.time()
    while time.time() - t0 < timeout:
        for cand in (res, res2):
            if os.path.exists(cand):
                return open(cand, encoding="utf-8").read()
        time.sleep(0.5)
    return '{"ok": false, "error": "timeout"}'


def run_file(path, timeout=1800, tag=None):
    with open(path, encoding="utf-8") as fh:
        return run(fh.read(), timeout=timeout, tag=tag)


if __name__ == "__main__":
    code = (
        "import maya.cmds as cmds, json, os\n"
        "OUT = r'%s'\n"
        "d = {'ver': cmds.about(version=1), 'scene': cmds.file(q=True, sn=True)}\n"
        "json.dump(d, open(os.path.join(OUT, 'logs', '_poller_test.json'), 'w', encoding='utf-8'), ensure_ascii=False)\n"
    ) % r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
    print(run(code, timeout=60, tag="pingtest"))
