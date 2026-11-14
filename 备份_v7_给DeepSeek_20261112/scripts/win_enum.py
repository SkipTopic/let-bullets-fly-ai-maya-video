import ctypes, ctypes.wintypes as w, sys

u = ctypes.windll.user32
EnumWindows = u.EnumWindows
GetWindowTextW = u.GetWindowTextW
GetClassNameW = u.GetClassNameW
GetWindowThreadProcessId = u.GetWindowThreadProcessId
IsWindowVisible = u.IsWindowVisible
EnumChildWindows = u.EnumChildWindows
SendMessageW = u.SendMessageW

PID = int(sys.argv[1]) if len(sys.argv) > 1 else None

WNDENUMPROC = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)

def text(hwnd):
    n = GetWindowTextW(hwnd, None, 0)
    buf = ctypes.create_unicode_buffer(n + 2)
    GetWindowTextW(hwnd, buf, n + 2)
    return buf.value

def cls(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    GetClassNameW(hwnd, buf, 256)
    return buf.value

results = []
@WNDENUMPROC
def cb(hwnd, lp):
    pid = w.DWORD()
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if PID is None or pid.value == PID:
        if IsWindowVisible(hwnd):
            results.append((hwnd, pid.value, cls(hwnd), text(hwnd)))
    return True

EnumWindows(cb, 0)
print("=== top-level windows ===")
for hwnd, pid, c, t in results:
    print(hex(hwnd), pid, repr(c), repr(t))

print("=== children ===")
for hwnd, pid, c, t in results:
    kids = []
    @WNDENUMPROC
    def cb2(h, lp):
        kids.append((h, cls(h), text(h)))
        return True
    EnumChildWindows(hwnd, cb2, 0)
    print("---", repr(t), hex(hwnd), "children:", len(kids))
    for h, kc, kt in kids[:40]:
        print("    ", hex(h), repr(kc), repr(kt))
