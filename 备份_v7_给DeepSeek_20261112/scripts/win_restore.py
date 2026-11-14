import ctypes, ctypes.wintypes as w
u = ctypes.windll.user32
for h, x, y in ((0x1b0520, 641, 282), (0x230604, 391, 135)):
    r = w.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    u.SetWindowPos(h, 0, x, y, r.right - r.left, r.bottom - r.top, 0x0040 | 0x0004)
    print("restored", hex(h), "->", x, y)
