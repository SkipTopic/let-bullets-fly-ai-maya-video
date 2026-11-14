# -*- coding: utf-8 -*-
"""Probe: does MEL command + python(io.open) work on port 50007?"""
import socket
import time

WORK = "C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"

# unicode-escape the Chinese parts so the wire payload is pure ASCII
esc = (
    "C:/Users/admin/Desktop/MayaProject/"
    + "".join("\\u%04x" % ord(c) for c in "让子弹飞分镜测试")
    + "/"
    + "".join("\\u%04x" % ord(c) for c in "工作区域文件夹")
    + "/logs/io_test.txt"
)

pycode = 'import io; io.open(r"%s","w",encoding="utf-8").write("io_ok")' % esc
mel = 'polySphere -n EP2; select EP2; python("%s")' % pycode.replace('"', '\\"')

s = socket.create_connection(("127.0.0.1", 50007), timeout=8)
s.settimeout(8)
s.sendall(mel.encode("ascii") + b"\n")
time.sleep(3)
s.close()
print("sent ascii-only command, len =", len(mel))
