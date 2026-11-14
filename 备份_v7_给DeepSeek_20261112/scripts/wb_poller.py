import os
import threading
import time

CMD_DIR = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\cmd"
POLL = 0.4
_STARTED = False


def _run(path):
    import traceback
    import maya.cmds as cmds

    key = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(CMD_DIR, "result_%s.json" % key)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            code = fh.read()
        g = {"__name__": "__maya_cmd__", "cmds": cmds}
        exec(compile(code, path, "exec"), g)
        payload = '{"ok": true}'
    except Exception:
        payload = '{"ok": false, "error": %r}' % traceback.format_exc()
    try:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(payload)
    except Exception:
        pass
    try:
        os.rename(path, os.path.join(CMD_DIR, "done_" + os.path.basename(path)))
    except Exception:
        pass


def _loop():
    import maya.utils

    while True:
        try:
            if os.path.isdir(CMD_DIR):
                for f in sorted(os.listdir(CMD_DIR)):
                    if f.startswith("cmd_") and f.endswith(".py"):
                        src = os.path.join(CMD_DIR, f)
                        dst = os.path.join(CMD_DIR, "run_" + f)
                        try:
                            os.rename(src, dst)   # 先抢走，避免被重复执行
                        except Exception:
                            continue
                        maya.utils.executeDeferred(_run, dst)
                        time.sleep(0.35)
        except Exception:
            pass
        time.sleep(POLL)


def start():
    global _STARTED
    if _STARTED:
        return False
    _STARTED = True
    os.makedirs(CMD_DIR, exist_ok=True)
    threading.Thread(target=_loop, name="wb_cmd_poller", daemon=True).start()
    return True
