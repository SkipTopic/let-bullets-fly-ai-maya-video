"""Maya commandPort driver.

注意：Maya 返回以 b'\\n\\x00' 结尾，不是纯换行。必须按"静默 0.25s 即认为收完"来读，
否则会一直阻塞 —— 上一轮就是被这个坑住的。
"""
import socket, time, os

HOST, PORT = "127.0.0.1", 50007


def mel(cmd, timeout=1800, quiet=0.25):
    s = socket.create_connection((HOST, PORT), timeout=10)
    s.setblocking(False)
    s.sendall((cmd + "\n").encode("utf-8"))
    buf = b""
    deadline = time.time() + timeout
    last = time.time()
    while time.time() < deadline:
        try:
            chunk = s.recv(65536)
            if chunk:
                buf += chunk
                last = time.time()
            else:
                break
        except BlockingIOError:
            if buf and (time.time() - last) > quiet:
                break
            time.sleep(0.02)
        except socket.error:
            break
    s.close()
    return buf.replace(b"\x00", b"").decode("utf-8", "replace").strip()


def run_py(script_path, timeout=3600, quiet=0.6):
    p = str(script_path).replace("\\", "/")
    cmd = ('python("exec(compile(open(\'%s\', encoding=\'utf-8\').read(), \'%s\', \'exec\'))")'
           % (p, p))
    return mel(cmd, timeout=timeout, quiet=quiet)


if __name__ == "__main__":
    print("ping:", repr(mel('python("1+1")')))
    print("ver :", repr(mel('python("import maya.cmds as c; print(c.about(version=1))")')))
