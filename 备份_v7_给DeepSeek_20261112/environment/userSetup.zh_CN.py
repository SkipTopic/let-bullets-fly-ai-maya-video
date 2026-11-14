# Maya 启动钩子
# 1) 保留 MayaMCP 用的 50007 命令端口
# 2) 启动单例文件轮询执行器（绕开命令端口安全弹窗）
import sys

import maya.cmds as cmds

MAYA_MCP_COMMAND_PORT = "127.0.0.1:50007"
SCRIPTS = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts"

try:
    try:
        cmds.commandPort(name=MAYA_MCP_COMMAND_PORT, close=True)
    except Exception:
        pass
    cmds.commandPort(
        name=MAYA_MCP_COMMAND_PORT,
        sourceType="mel",
        echoOutput=True,
        multiClient=True,
        securityWarning=False,
    )
    print("MayaMCP: command port listening on " + MAYA_MCP_COMMAND_PORT)
except Exception as exc:
    print("MayaMCP: command port not opened ({0})".format(exc))

try:
    if SCRIPTS not in sys.path:
        sys.path.insert(0, SCRIPTS)
    import wb_poller

    if wb_poller.start():
        print("[wb] file command poller started")
    else:
        print("[wb] poller already running")
except Exception as exc:
    print("[wb] poller failed: %r" % (exc,))
