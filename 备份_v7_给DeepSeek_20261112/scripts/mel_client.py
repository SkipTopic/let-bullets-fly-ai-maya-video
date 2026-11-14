# -*- coding: utf-8 -*-
"""Maya commandPort client.

Sends MEL commands to a running Maya GUI via commandPort 127.0.0.1:50007.
Maya may crash if we use mayapy/mayabatch on this machine, so ALL python
code must be executed inside the running GUI through this port.

Usage:
    from mel_client import mel, py
    print(mel('python("1+1")'))
    print(py('import maya.cmds as cmds; print(len(cmds.ls()))'))
"""
import base64
import socket

HOST, PORT = "127.0.0.1", 50007


def mel(cmd, timeout=300):
    """Send one MEL command, return Maya's reply text.

    Maya's reply ends with b"\\n\\x00" (result + NUL); older no-echo
    setups returned nothing. Accept either.
    """
    s = socket.create_connection((HOST, PORT), timeout=timeout)
    s.settimeout(timeout)
    s.sendall((cmd + "\n").encode("utf-8"))
    buf = b""
    while not (buf.endswith(b"\n\x00") or buf.endswith(b"\n\x00\n")):
        c = s.recv(65536)
        if not c:
            break
        buf += c
        if buf.endswith(b"\x00"):
            break
    s.close()
    return buf.decode("utf-8", "replace").rstrip("\x00\n")


def _quote_for_mel(s):
    """Escape a python one-liner into a MEL double-quoted string."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def py(code, timeout=600, capture=True):
    """Run python code inside Maya, return its stdout (captured) or repr."""
    b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
    if capture:
        # single-line wrapper: exec user code, return captured stdout
        one = (
            'import base64, io, contextlib;_b = io.StringIO();'
            '_o = contextlib.redirect_stdout(_b);_o.__enter__();'
            'exec(base64.b64decode("%s").decode("utf-8"));'
            '_o.__exit__(None, None, None);_b.getvalue()' % b64
        )
    else:
        one = (
            'import base64;exec(base64.b64decode("%s").decode("utf-8"))' % b64
        )
    r = mel('python("%s")' % _quote_for_mel(one), timeout=timeout)
    return r


if __name__ == "__main__":
    import sys
    t = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    try:
        print("REPLY:", mel('python("1+1")', timeout=t))
    except Exception as e:
        print("FAIL:", type(e).__name__, e)
        sys.exit(1)
