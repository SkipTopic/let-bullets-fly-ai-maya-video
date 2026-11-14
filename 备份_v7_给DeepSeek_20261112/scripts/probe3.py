# -*- coding: utf-8 -*-
"""Probe 3: full validation of port channel - python result, UTF-8 paths, io.open."""
import socket
import time
import sys

sys.path.insert(0, r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts")
from mel_client import mel, py

# 1) python result return
print("python 1+1 ->", repr(mel('python("1+1")')))

# 2) MEL fopen with real UTF-8 Chinese path
work = "C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"
cmd = '$h=`fopen "%s/logs/mel_test.txt" "w"`;fprint $h "mel_write_ok";fclose $h;' % work
r = mel(cmd)
print("fopen reply ->", repr(r))

# 3) python io.open with real UTF-8 Chinese path
code = "import io; f=io.open(r'%s/logs/py_io_test.txt','w',encoding='utf-8'); f.write('py_io_ok'); f.close(); print('written')" % work
r = py(code)
print("py io.open ->", repr(r))

# 4) python print return via capture
r = py("x=41+1; print(x)")
print("py print ->", repr(r))
