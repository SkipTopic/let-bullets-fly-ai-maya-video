import ctypes, time, sys
u = ctypes.windll.user32
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    u.SetProcessDPIAware()

x, y = int(sys.argv[1]), int(sys.argv[2])
u.SetCursorPos(x, y)
time.sleep(0.25)
u.mouse_event(0x0002, 0, 0, 0, 0)  # down
time.sleep(0.06)
u.mouse_event(0x0004, 0, 0, 0, 0)  # up
print("clicked", x, y)
