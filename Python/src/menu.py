import sys
import time
import pygame
from radio_controller import RadioController
from utils import save_config, get_axis_idx

# ══════════════ MENU IMPOSTAZIONI ══════════════
MENU_ITEMS = [
    {"label": "TX Power (dBm)",     "key": "tx_power",  "type": "slider", "min": -5,  "max": 20,  "step": 1},
    {"label": "Send Rate (Hz)",     "key": "send_rate", "type": "slider", "min": 1,   "max": 100, "step": 1},
    {"label": "Livelli Velocità",   "key": "max_speeds","type": "slider", "min": 0,   "max": 16,  "step": 1},
    {"label": "Angolo Max Sterzo",  "key": "STEERING_MAX_ANGLE", "type": "slider", "min": 10, "max": 180, "step": 5},
    {"label": "Gradi Volante",      "key": "WHEEL_RANGE_DEGREES","type": "slider", "min": 90, "max": 900, "step": 10},
    {"label": "Calibra Zero Servo", "key": "calibrate",  "type": "action"},
    {"label": "Porta Seriale",      "key": "serial_port", "type": "info"},
    {"label": "Rimappa Controller", "key": "remap",       "type": "action"},
    {"label": "Refresh Status TX",  "key": "refresh",     "type": "action"},
    {"label": "Chiudi Programma",   "key": "quit",        "type": "action"},
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

# ══════════════ CALIBRAZIONE ZERO SERVO ══════════════
def display_calibration(offset: float, volante_deg: float, steering_max: float):
    W = 60
    sep = "=" * W
    mid = "-" * W
    def pad(s): return s.ljust(W)

    # visual bar for offset
    bar_w = 40
    center = bar_w // 2
    pos = int(offset / steering_max * center)
    pos = max(-center, min(center, pos))
    bar = [' '] * bar_w
    bar[center] = '|'
    marker = center + pos
    marker = max(0, min(bar_w - 1, marker))
    bar[marker] = '#'
    bar_str = '[' + ''.join(bar) + ']'

    lines = [
        "\033[H", sep,
        pad("       CALIBRAZIONE ZERO SERVO"), sep,
        pad("  Gira il volante per regolare l'offset"),
        pad("  VEL_SU / VEL_GIU = ±1°  (fine tuning)"),
        pad("  RETRO = Conferma e Salva"),
        pad("  MENU  = Annulla"), mid,
        pad(f"  Offset attuale : {offset:+.1f}°"),
        pad(f"  Volante (gradi) : {volante_deg:+.1f}°"),
        pad(f"  Range max      : ±{steering_max:.0f}°"),
        pad(f"  {bar_str}"),
        mid,
        pad(f"  Servo centro → byte {int(128 + (offset / steering_max) * 127) if steering_max else 128}"),
    ]
    while len(lines) < 20:
        lines.append(pad(""))
    lines.append(sep)
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


def run_servo_calibration(js, assi: dict, pulsanti: dict, rc: RadioController, cfg: dict) -> float:
    """Interactive servo zero calibration. Returns the new offset (degrees)."""
    sterzo_idx = get_axis_idx(assi, "STERZO")
    wheel_range = cfg.get("WHEEL_RANGE_DEGREES", 450)
    steering_max = cfg.get("STEERING_MAX_ANGLE", 90)
    offset = cfg.get("SERVO_ZERO_OFFSET", 0)

    # The wheel controls the offset: map wheel to ±steering_max/2 range
    calibration_range = steering_max  # max offset = full steering range

    press_threshold = 0.08
    hold_start: dict[int, float] = {}

    # Wait for previous button release
    menu_idx = pulsanti.get("MENU")
    retro_idx = pulsanti.get("RETRO")
    if retro_idx is not None:
        t0 = time.time()
        while time.time() - t0 < 0.5:
            pygame.event.pump()
            if not js.get_button(retro_idx):
                break
            time.sleep(0.02)
    pygame.event.clear()
    time.sleep(0.15)

    # keyboard non-blocking
    if sys.platform == "win32":
        import msvcrt
    else:
        import select, tty, termios
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    def read_key():
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

    confirmed = False
    original_offset = offset
    use_wheel = True  # wheel controls offset by default

    display_calibration(offset, 0, steering_max)

    try:
        while True:
            action = None
            now = time.time()
            pygame.event.pump()

            # Read wheel position
            volante = js.get_axis(sterzo_idx)
            volante_deg = volante * (wheel_range / 2)

            # Wheel directly maps to offset (scaled to calibration range)
            if use_wheel:
                offset = volante * calibration_range
                offset = max(-calibration_range, min(calibration_range, offset))

            # Gamepad events
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
                                action = nome
                            break

            # Keyboard
            key = read_key()
            if key == "UP":    action = "VEL_SU"
            elif key == "DOWN": action = "VEL_GIU"
            elif key == "LEFT":
                offset = max(-calibration_range, offset - 1)
                use_wheel = False
            elif key == "RIGHT":
                offset = min(calibration_range, offset + 1)
                use_wheel = False
            elif key == "ENTER": action = "RETRO"
            elif key == "ESC":   action = "MENU"

            if action == "VEL_SU":
                offset = min(calibration_range, offset + 1)
                use_wheel = False  # switch to manual fine-tuning
            elif action == "VEL_GIU":
                offset = max(-calibration_range, offset - 1)
                use_wheel = False
            elif action == "RETRO":
                confirmed = True
                break
            elif action == "MENU":
                offset = original_offset
                break

            # Send center position to servo in real-time (if connected)
            if rc.connected:
                center_byte = int(128 + (offset / steering_max) * 127)
                center_byte = max(0, min(255, center_byte))
                rc.send_data(center_byte, 0, False, 0, False, 0)

            display_calibration(offset, volante_deg, steering_max)
            time.sleep(0.03)
    finally:
        if sys.platform != "win32":
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    if confirmed:
        offset = round(offset, 1)
        cfg["SERVO_ZERO_OFFSET"] = offset
        save_config({"SERVO_ZERO_OFFSET": offset})

    return offset


def run_menu(js, pulsanti: dict, assi: dict, rc: RadioController, cfg: dict) -> dict:
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
    nav_up_idx = pulsanti.get("VEL_SU")
    nav_down_idx = pulsanti.get("VEL_GIU")

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

    # Chiavi che vanno persistite in config.json
    CONFIG_BACKED_KEYS = {"STEERING_MAX_ANGLE", "WHEEL_RANGE_DEGREES"}

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
        if key in CONFIG_BACKED_KEYS:
            save_config({key: new})
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
                                if nome in ("VEL_SU", "VEL_GIU"):
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
                            if nome in ("VEL_SU", "VEL_GIU"):
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
            if key == "UP":    action = "VEL_SU"
            elif key == "DOWN": action = "VEL_GIU"
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
            elif action == "VEL_SU":
                if editing and MENU_ITEMS[cursor].get("type") == "slider":
                    if adjust_current(-1): display_menu(cursor, rc, cfg, editing)
                else:
                    cursor = (cursor - 1) % len(MENU_ITEMS)
            elif action == "VEL_GIU":
                if editing and MENU_ITEMS[cursor].get("type") == "slider":
                    if adjust_current(+1): display_menu(cursor, rc, cfg, editing)
                else:
                    cursor = (cursor + 1) % len(MENU_ITEMS)
            elif action == "RETRO":
                item = MENU_ITEMS[cursor]
                if item.get("type") == "slider":
                    editing = not editing
                elif item.get("type") == "action":
                    if item["key"] == "calibrate":
                        run_servo_calibration(js, assi, pulsanti, rc, cfg)
                        from utils import clear_once
                        clear_once()
                    elif item["key"] == "remap":
                        need_remap = True
                        break
                    elif item["key"] == "refresh" and rc.connected:
                        rc.refresh_status()
                    elif item["key"] == "quit":
                        cfg["_quit"] = True
                        break
                    elif item["key"] == "exit":
                        break
                display_menu(cursor, rc, cfg, editing)

            # assicurati che il menu venga ridisegnato anche quando si naviga
            display_menu(cursor, rc, cfg, editing)

            time.sleep(0.03)
    finally:
        if sys.platform != "win32":
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    cfg["_need_remap"] = need_remap
    return cfg