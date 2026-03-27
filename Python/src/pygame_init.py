import os
import sys
import pygame

# ══════════════ PYGAME INIT ══════════════
def init_pygame():
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    if sys.platform == "win32":
        os.environ["SDL_VIDEO_WINDOW_POS"] = "-32000,-32000"
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        try:
            import ctypes
            hwnd = pygame.display.get_wm_info()["window"]
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x00000080)
        except Exception:
            pass
    else:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.display.init()
        pygame.joystick.init()