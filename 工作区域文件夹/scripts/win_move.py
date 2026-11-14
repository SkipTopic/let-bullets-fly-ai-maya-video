import ctypes, ctypes.wintypes as w, sys, subprocess

u = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
pid_target = int(sys.argv[1])
dst = (int(sys.argv[2]), int(sys.argv[3]))

def get_rect(h):
    r = w.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    return r.left, r.top, r.right - r.left, r.bottom - r.top

found = []
@WNDENUMPROC
def cb(h, lp):
    pid = w.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(pid))
    if pid.value != pid_target or not u.IsWindowVisible(h):
        return True
    x, y, ww, hh = get_rect(h)
    if 100 < ww < 900 and 80 < hh < 800:
        found.append((h, x, y, ww, hh))
    return True

u.EnumWindows(cb, 0)
print("candidates", [(hex(h), x, y, ww, hh) for h, x, y, ww, hh in found])
for h, x, y, ww, hh in found:
    u.SetWindowPos(h, 0, dst[0], dst[1], ww, hh, 0x0040 | 0x0004 | 0x0010)
    print("moved", hex(h), "->", dst)
