import pygame
import time
import sys
import argparse
import json
import pathlib
import serial
import struct
import os

# --- COSTANTI DI DEFAULT (In assenza di config.json) ---
DEFAULT_CONFIG = {
    "SERIAL_BAUD": 115200,
    "MAX_SPEEDS": 6,
    "DISPLAY_REFRESH_S": 0.1,
    "MAPPING_FILE": "mapping.json",
    "DEFAULT_SEND_RATE": 30,
    "BINARY_MARKER": 0xAA,
    "DEFAULT_TX_POWER": 10
}

# Caricamento configurazione
try:
    with open(pathlib.Path(__file__).parent / "config.json") as f:
        config = {**DEFAULT_CONFIG, **json.load(f)}
except Exception:
    config = DEFAULT_CONFIG

# ══════════════ UTILS & CRC ══════════════
def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if (crc & 0x8000) else (crc << 1)
            crc &= 0xFFFF
    return crc

def clear_once():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

# ══════════════ RADIO CONTROLLER ══════════════
class RadioController:
    def __init__(self):
        self.ser: serial.Serial | None = None
        self.module = "UNKNOWN"
        self.send_rate = config['DEFAULT_SEND_RATE']
        self.tx_power = config['DEFAULT_TX_POWER']
        self.connected = False
        self.tx_count = 0
        self.tx_fail = 0

    def connect(self, port: str, baud: int) -> bool:
        try:
            self.ser = serial.Serial(port, baud, timeout=0.1)
            time.sleep(2)
            self.ser.reset_input_buffer()
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            return False

    def send_command(self, cmd: str) -> str | None:
        if not self.ser: return None
        try:
            self.ser.reset_input_buffer()
            self.ser.write((cmd + "\n").encode())
            time.sleep(0.15)
            return self.ser.readline().decode(errors="replace").strip() or None
        except Exception: return None

    def handshake(self) -> bool:
        resp = self.send_command("HANDSHAKE")
        if resp and resp.startswith("ACK"):
            self._parse_status(resp.split())
            return True
        return False

    def _parse_status(self, parts: list[str]):
        if len(parts) >= 2: self.module = parts[1]
        if len(parts) >= 3: self.send_rate = int(parts[2])
        if len(parts) >= 4: self.tx_power = int(parts[3])

    def send_data(self, steer: int, accel: int, brake: bool, speed_sel: int, reverse: bool, commands: int):
        if not self.ser: return
        misc = ((speed_sel & 0x0F) << 4) | ((1 if brake else 0) << 3) | ((1 if reverse else 0) << 2) | (commands & 0x03)
        payload = bytes([steer, accel, misc])
        crc = crc16_ccitt(payload)
        frame = bytes([config['BINARY_MARKER']]) + payload + struct.pack(">H", crc)
        try:
            self.ser.write(frame)
            self.tx_count += 1
        except: self.tx_fail += 1

    def poll_messages(self):
        msgs = []
        while self.ser and self.ser.in_waiting:
            line = self.ser.readline().decode(errors="replace").strip()
            if line: msgs.append(line)
        return msgs

    def close(self):
        if self.ser: self.ser.close()

# ══════════════ DISCOVERY & MAPPING ══════════════
def load_mapping():
    p = pathlib.Path(config['MAPPING_FILE'])
    if p.exists():
        with open(p) as f: return json.load(f)
    return None

def save_mapping(data):
    with open(config['MAPPING_FILE'], "w") as f: json.dump(data, f, indent=2)

def scopri_assi(js):
    print(f"\n  Mapping Assi per: {js.get_name()}")
    nomi = ["STERZO", "ACCELERATORE", "FRENO"]
    assi = {}
    for nome in nomi:
        print(f"  Muovi {nome}...", end="", flush=True)
        baseline = [js.get_axis(i) for i in range(js.get_numaxes())]
        found = False
        t0 = time.time()
        while time.time() - t0 < 10 and not found:
            pygame.event.pump()
            for i in range(js.get_numaxes()):
                if abs(js.get_axis(i) - baseline[i]) > 0.5:
                    assi[nome] = i
                    print(f" OK (Asse {i})")
                    found = True
                    time.sleep(0.5)
                    break
        if not found: print(" Timeout!")
    return assi

def scopri_pulsanti(js):
    print("\n  Mapping Pulsanti...")
    nomi = ["MARCIA_SU", "MARCIA_GIU", "RETRO", "MENU"]
    btns = {}
    for nome in nomi:
        print(f"  Premi {nome}...", end="", flush=True)
        found = False
        t0 = time.time()
        while time.time() - t0 < 10 and not found:
            pygame.event.pump()
            for i in range(js.get_numbuttons()):
                if js.get_button(i):
                    btns[nome] = i
                    print(f" OK (Btn {i})")
                    found = True
                    time.sleep(0.5)
                    break
    return btns

# ══════════════ MENU & DISPLAY ══════════════
def display(rc, volante, accel, brake, speed_sel, reverse, actual_rate, log_lines, max_speeds):
    sys.stdout.write("\033[H")
    W = 60
    print("=" * W)
    print(f"  SQUADRA CORSE TX | Modulo: {rc.module}".ljust(W))
    print("=" * W)
    print(f"  Rate: {actual_rate:.0f}/{rc.send_rate} Hz | PKT: {rc.tx_count}".ljust(W))
    print(f"  Steer: {volante:+6.2f} | Accel: {accel:4.2f} | Brake: {brake:4.2f}".ljust(W))
    mode = "RETRO" if reverse else "AVANTI"
    print(f"  Marcia: {speed_sel+1}/{max_speeds} [{mode}]".ljust(W))
    print("-" * W)
    for line in log_lines[-4:]:
        print(f"  >> {line}".ljust(W))
    print("=" * W)
    print("  [MENU] Impostazioni | CTRL+C per uscire".ljust(W))

def run_menu(js, pulsanti, rc, cfg):
    cursor = 0
    items = [
        {"l": "TX Power", "k": "tx_power", "min": -5, "max": 20},
        {"l": "Send Rate", "k": "send_rate", "min": 1, "max": 100},
        {"l": "Max Marce", "k": "max_speeds", "min": 1, "max": 16},
        {"l": "Esci", "k": "exit"}
    ]
    
    clear_once()
    while True:
        sys.stdout.write("\033[H")
        print("=== MENU IMPOSTAZIONI ===")
        for i, item in enumerate(items):
            prefix = " > " if i == cursor else "   "
            val = cfg.get(item['k'], "")
            print(f"{prefix} {item['l']}: {val}")
        
        pygame.event.pump()
        # Navigazione semplificata per il menu
        time.sleep(0.1)
        if js.get_button(pulsanti["MARCIA_SU"]):
            cursor = (cursor - 1) % len(items)
        if js.get_button(pulsanti["MARCIA_GIU"]):
            cursor = (cursor + 1) % len(items)
        if js.get_button(pulsanti["RETRO"]): # Usato come "Enter"
            target = items[cursor]
            if target['k'] == "exit": break
            # Logica cambio valori (semplificata)
            cfg[target['k']] = min(target['max'], cfg[target['k']] + 1)
        if js.get_button(pulsanti["MENU"]): break
    
    clear_once()
    return cfg

# ══════════════ MAIN ══════════════
def main():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("Nessun controller!")
        return
    
    js = pygame.joystick.Joystick(0)
    js.init()

    mapping = load_mapping()
    if not mapping or mapping.get("controller") != js.get_name():
        assi = scopri_assi(js)
        btns = scopri_pulsanti(js)
        mapping = {"controller": js.get_name(), "assi": assi, "pulsanti": btns}
        save_mapping(mapping)

    rc = RadioController()
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs="?", default="COM9" if sys.platform == "win32" else "/dev/ttyUSB0")
    args = parser.parse_args()

    rc.connect(args.port, config['SERIAL_BAUD'])
    rc.handshake()

    # Stato iniziale
    speed_sel = 0
    reverse = False
    log_lines = []
    last_display = 0
    
    clear_once()
    try:
        while True:
            pygame.event.pump()
            
            # Gestione Pulsanti (Marce e Menu)
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == mapping["pulsanti"]["MARCIA_SU"]:
                        speed_sel = min(config["MAX_SPEEDS"]-1, speed_sel + 1)
                    if event.button == mapping["pulsanti"]["MARCIA_GIU"]:
                        speed_sel = max(0, speed_sel - 1)
                    if event.button == mapping["pulsanti"]["RETRO"]:
                        reverse = not reverse
                    if event.button == mapping["pulsanti"]["MENU"]:
                        run_menu(js, mapping["pulsanti"], rc, config)

            # Lettura Assi
            steer_val = js.get_axis(mapping["assi"]["STERZO"])
            accel_val = (js.get_axis(mapping["assi"]["ACCELERATORE"]) + 1) / 2
            brake_val = (js.get_axis(mapping["assi"]["FRENO"]) + 1) / 2
            
            # Trasmissione
            steer_byte = int((steer_val + 1) * 127.5)
            accel_byte = int(accel_val * 255)
            rc.send_data(steer_byte, accel_byte, brake_val > 0.1, speed_sel, reverse, 0)

            # Display
            now = time.time()
            if now - last_display > config["DISPLAY_REFRESH_S"]:
                display(rc, steer_val, accel_val, brake_val, speed_sel, reverse, 0, log_lines, config["MAX_SPEEDS"])
                last_display = now
            
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        rc.close()
        pygame.quit()

if __name__ == "__main__":
    main()