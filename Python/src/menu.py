import sys
import time
import pygame
from radio_controller import RadioController

# ══════════════ MENU IMPOSTAZIONI ══════════════
MENU_ITEMS = [
    {"label": "TX Power (dBm)",     "key": "tx_power",  "type": "slider", "min": -5,  "max": 20,  "step": 1},
    {"label": "Send Rate (Hz)",     "key": "send_rate", "type": "slider", "min": 1,   "max": 100, "step": 1},
    {"label": "Max Marce",          "key": "max_speeds","type": "slider", "min": 0,   "max": 16,  "step": 1},
    {"label": "Porta Seriale",      "key": "serial_port", "type": "info"},
    {"label": "Rimappa Controller", "key": "remap",       "type": "action"},
    {"label": "Refresh Status TX",  "key": "refresh",     "type": "action"},
    {"label": "Esci dal menu",      "key": "exit",        "type": "action"},
]

def display_menu(cursor: int, rc: RadioController, cfg: dict, editing: bool = False):
    W = 60
    sep = "=" * W
    mid = "-" * W
    def pad(s): return s.ljust(W)
    def slider_bar(val, mn, mx, width=28):
        if mx <= mn: return '[' + ' ' * width + ']'
        pos = int((val - mn) / (mx - mn) * width)
        pos = max(0, min(width, pos))
        return '[' + ('=' * pos).ljust(width) + ']'

    lines = ["\033[H", sep, pad("       IMPOSTAZIONI"), sep,
             pad("  PAD: SU/GIU = naviga | RETRO = entra/esci edit"),
             pad("  TAST: Frecce = naviga | ←/→ = cambia | INVIO = entra/esci"), mid]

    for i, item in enumerate(MENU_ITEMS):
        prefix = " >>" if i == cursor else "   "
        label = item["label"]
        key = item.get("key")
        if item["type"] == "slider":
            mn = item.get("min", 0)
            mx = item.get("max", 100)
            cur = cfg.get(key, mn)
            bar = slider_bar(cur, mn, mx)
            edit_tag = " <EDIT>" if i == cursor and editing else ""
            line = f"{prefix} {label}: {bar} {cur}{edit_tag}"
        elif item["type"] == "info" and key == "serial_port":
            line = f"{prefix} {label}: {cfg.get('serial_port')}"
        elif item["type"] == "action":
            line = f"{prefix} {label}"
        else:
            line = f"{prefix} {label}: {cfg.get(key, '')}"
        lines.append(pad(line))

    while len(lines) < 20:
        lines.append(pad(""))
    lines.append(sep)
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()

def run_menu(js, pulsanti: dict, rc: RadioController, cfg: dict) -> dict:
    cursor = 0
    editing = False
    need_remap = False

    # throttle e hold-repeat (stessi valori originali)
    hold_delay = 0.60
    repeat_interval = 0.35
    nav_hold_delay = 0.45
    nav_repeat_interval = 0.20
    enter_edit_threshold = 1.0
    # tempo minimo di pressione per confermare l'azione (pressione "leggermente più lunga")
    press_threshold = 0.08

    retro_idx = pulsanti.get("RETRO")
    nav_up_idx = pulsanti.get("MARCIA_SU")
    nav_down_idx = pulsanti.get("MARCIA_GIU")

    retro_hold_start = nav_hold_start = enter_hold_start = None
    retro_next_repeat = nav_next_repeat = enter_last_repeat = 0.0
    last_nav_press = last_retro_press = 0.0
    # hold timer per singoli pulsanti (index -> start_time)
    hold_start: dict[int, float] = {}

    # scarica MENU che ha aperto il menu
    menu_idx = pulsanti.get("MENU")
    if menu_idx is not None:
        t0 = time.time()
        while time.time() - t0 < 0.5:
            pygame.event.pump()
            if not js.get_button(menu_idx):
                break
            time.sleep(0.02)

    pygame.event.clear()
    time.sleep(0.15)

    # tastiera non-bloccante
    if sys.platform == "win32":
        import msvcrt
    else:
        import select, tty, termios
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    def read_key() -> str | None:
        if sys.platform == "win32":
            if not msvcrt.kbhit(): return None
            ch = msvcrt.getch()
            if ch in (b'\xe0', b'\x00'):
                ch2 = msvcrt.getch()
                if ch2 == b'H': return "UP"
                if ch2 == b'P': return "DOWN"
                if ch2 == b'K': return "LEFT"
                if ch2 == b'M': return "RIGHT"
            if ch == b'\r': return "ENTER"
            if ch == b'\x1b': return "ESC"
            return None
        else:
            if select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    if select.select([sys.stdin], [], [], 0.05)[0]:
                        ch2 = sys.stdin.read(1)
                        if ch2 == '[' and select.select([sys.stdin], [], [], 0.05)[0]:
                            ch3 = sys.stdin.read(1)
                            if ch3 == 'A': return "UP"
                            if ch3 == 'B': return "DOWN"
                            if ch3 == 'C': return "RIGHT"
                            if ch3 == 'D': return "LEFT"
                    return "ESC"
                if ch in ('\n', '\r'): return "ENTER"
            return None

    def adjust_current(delta: int) -> bool:
        item = MENU_ITEMS[cursor]
        if item.get("type") != "slider": return False
        key = item["key"]
        mn, mx, step = item.get("min", 0), item.get("max", 100), item.get("step", 1)
        cur = cfg.get(key, mn)
        new = max(mn, min(mx, cur + delta * step))
        if new == cur: return False
        cfg[key] = new
        if key == "tx_power" and rc.connected:
            rc.set_tx_power(new)
        if key == "send_rate" and rc.connected:
            rc.set_send_rate(new)
        return True

    display_menu(cursor, rc, cfg, editing)

    try:
        while True:
            action = None
            now = time.time()

            # gamepad eventi: usa press/hold-release per richiedere durata minima
            for ev in pygame.event.get():
                if ev.type == pygame.JOYBUTTONDOWN:
                    for nome, idx in pulsanti.items():
                        if ev.button == idx:
                            hold_start[idx] = now
                            break
                elif ev.type == pygame.JOYBUTTONUP:
                    for nome, idx in pulsanti.items():
                        if ev.button == idx:
                            start = hold_start.pop(idx, None)
                            if start is not None and now - start >= press_threshold:
                                if nome in ("MARCIA_SU", "MARCIA_GIU"):
                                    action = nome
                                    last_nav_press = now
                                elif nome == "RETRO":
                                    action = nome
                                    last_retro_press = now
                                else:
                                    action = nome
                            break

            # polling fallback + hold: avvia il timer alla pressione e conferma all'uscita se durata sufficiente
            pygame.event.pump()
            for nome, idx in pulsanti.items():
                pressed = bool(js.get_button(idx))
                if pressed:
                    if idx not in hold_start:
                        hold_start[idx] = now
                else:
                    if idx in hold_start:
                        start = hold_start.pop(idx)
                        if now - start >= press_threshold:
                            if nome in ("MARCIA_SU", "MARCIA_GIU"):
                                action = nome
                                last_nav_press = now
                            elif nome == "RETRO":
                                action = nome
                                last_retro_press = now
                            else:
                                action = nome

            # hold repeat RETRO → enter edit
            if retro_idx is not None and js.get_button(retro_idx):
                if retro_hold_start is None:
                    retro_hold_start = now
                    retro_next_repeat = now + hold_delay
                elif now - retro_hold_start >= enter_edit_threshold and not editing:
                    editing = True
                    display_menu(cursor, rc, cfg, editing)
            else:
                retro_hold_start = None

            # hold repeat nav: disabled for immediate execution — navigation will occur on release
            # (up/down actions are performed when JOYBUTTONUP or polling release exceeds threshold)

            # tastiera
            key = read_key()
            if key == "UP":    action = "MARCIA_SU"
            elif key == "DOWN": action = "MARCIA_GIU"
            elif key == "LEFT" and editing:
                if adjust_current(-1): display_menu(cursor, rc, cfg, editing)
            elif key == "RIGHT" and editing:
                if adjust_current(+1): display_menu(cursor, rc, cfg, editing)
            elif key == "ENTER":
                action = "RETRO"
            elif key == "ESC":
                action = "MENU"

            if action == "MENU":
                break
            elif action == "MARCIA_SU":
                if editing and MENU_ITEMS[cursor].get("type") == "slider":
                    if adjust_current(-1): display_menu(cursor, rc, cfg, editing)
                else:
                    cursor = (cursor - 1) % len(MENU_ITEMS)
            elif action == "MARCIA_GIU":
                if editing and MENU_ITEMS[cursor].get("type") == "slider":
                    if adjust_current(+1): display_menu(cursor, rc, cfg, editing)
                else:
                    cursor = (cursor + 1) % len(MENU_ITEMS)
            elif action == "RETRO":
                item = MENU_ITEMS[cursor]
                if item.get("type") == "slider":
                    editing = not editing
                elif item.get("type") == "action":
                    if item["key"] == "remap":
                        need_remap = True
                        break
                    elif item["key"] == "refresh" and rc.connected:
                        rc.refresh_status()
                    elif item["key"] == "exit":
                        break
                display_menu(cursor, rc, cfg, editing)

            # assicurati che il menu venga ridisegnato anche quando si naviga
            display_menu(cursor, rc, cfg, editing)

            time.sleep(0.03)
    finally:
        if sys.platform != "win32":
            termios.tcgetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    cfg["_need_remap"] = need_remap
    return cfg