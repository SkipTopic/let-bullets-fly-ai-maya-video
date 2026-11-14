# -*- coding: utf-8 -*-
"""Probe 2: echo behavior + MEL fopen/fprint file write."""
import socket
import time

def send_recv(cmd, wait=6):
    s = socket.create_connection(("127.0.0.1", 50007), timeout=10)
    s.settimeout(wait)
    s.sendall(cmd.encode("ascii") + b"\n")
    buf = b""
    t0 = time.time()
    try:
        while time.time() - t0 < wait:
            c = s.recv(65536)
            if not c:
                break
            buf += c
    except Exception as e:
        pass
    s.close()
    return buf

# 1) does echoOutput send anything back for a MEL command?
r1 = send_recv('currentTime -q;')
print("RECV after 'currentTime -q':", repr(r1[:200]))

# 2) MEL fopen/fprint/fclose write test (ASCII-only path)
path = "C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹/logs/mel_test.txt"
esc = (
    "C:/Users/admin/Desktop/MayaProject/"
    + "".join("\\u%04x" % ord(c) for c in "让子弹飞分镜测试")
    + "/"
    + "".join("\\u%04x" % ord(c) for c in "工作区域文件夹")
    + "/logs/mel_test.txt"
)
cmd = '$h=`fopen "%s" "w"`;fprint $h "mel_write_ok";fclose $h;' % esc
r2 = send_recv(cmd)
print("RECV after fopen/fprint:", repr(r2[:200]))
print("mel cmd:", cmd)
