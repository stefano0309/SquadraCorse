import serial
import struct
import time
from config import SERIAL_BAUD, DEFAULT_SEND_RATE, BINARY_MARKER
from crc import crc16_ccitt

# ══════════════ RADIO CONTROLLER ══════════════
class RadioController:
    def __init__(self):
        self.ser: serial.Serial | None = None
        self.module = "UNKNOWN"
        self.send_rate = DEFAULT_SEND_RATE
        self.tx_power = 20
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
        except serial.SerialException as e:
            print(f"  Errore seriale: {e}")
            self.connected = False
            return False

    def send_command(self, cmd: str) -> str | None:
        if not self.ser: return None
        try:
            self.ser.reset_input_buffer()
            self.ser.write((cmd + "\n").encode())
            time.sleep(0.15)
            return self.ser.readline().decode(errors="replace").strip() or None
        except Exception:
            return None

    def handshake(self) -> bool:
        if self.ser:
            deadline = time.time() + 3
            while time.time() < deadline:
                if self.ser.in_waiting:
                    if self.ser.readline().decode(errors="replace").strip() == "READY":
                        break
                time.sleep(0.05)
        resp = self.send_command("HANDSHAKE")
        if resp and resp.startswith("ACK"):
            self._parse_status(resp.split())
            return True
        return False

    def refresh_status(self):
        resp = self.send_command("STATUS")
        if resp and resp.startswith("STATUS"):
            self._parse_status(resp.split())

    def set_tx_power(self, power: int) -> bool:
        if self.send_command(f"SET TXPOWER {power}") == "OK":
            self.tx_power = power
            return True
        return False

    def set_send_rate(self, rate: int) -> bool:
        if self.send_command(f"SET SENDRATE {rate}") == "OK":
            self.send_rate = rate
            return True
        return False

    def _parse_status(self, parts: list[str]):
        if len(parts) >= 3:
            self.module = parts[1]
            try: self.send_rate = int(parts[2])
            except: pass
        if len(parts) >= 4:
            try: self.tx_power = int(parts[3])
            except: pass

    def send_data(self, steer: int, accel: int, brake: int, speed_sel: int, reverse: bool, commands: int) -> bool:
        if not self.ser: return False
        steer = max(0, min(255, steer))
        accel = max(0, min(255, accel))
        brake = max(0, min(255, brake))
        speed_sel = max(0, min(15, speed_sel))
        commands = max(0, min(7, commands))
        misc = ((speed_sel & 0x0F) << 4) | ((1 if reverse else 0) << 3) | (commands & 0x07)
        payload = bytes([steer, accel, brake, misc])
        crc = crc16_ccitt(payload)
        frame = bytes([BINARY_MARKER]) + payload + struct.pack(">H", crc)
        try:
            self.ser.write(frame)
            self.tx_count += 1
            return True
        except Exception:
            self.tx_fail += 1
            return False

    def poll_messages(self) -> list[str]:
        msgs: list[str] = []
        while self.ser and self.ser.in_waiting:
            try:
                line = self.ser.readline().decode(errors="replace").strip()
                if not line: continue
                if line.startswith("MODULE_CHANGED"):
                    parts = line.split()
                    if len(parts) >= 2: self.module = parts[1]
                    if len(parts) >= 3:
                        try: self.tx_power = int(parts[2])
                        except: pass
                elif "FAIL" in line or "ERR" in line:
                    self.tx_fail += 1
                msgs.append(line)
            except Exception:
                break
        return msgs

    def close(self):
        if self.ser:
            self.ser.close()
            self.ser = None
        self.connected = False