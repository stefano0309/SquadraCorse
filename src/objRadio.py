import os
import struct
import time

import serial

from src.utils import crc16_ccitt, readfile


class RadioController:
    def __init__(self):
        self.config = readfile(os.path.join(os.path.dirname(__file__), "data", "radioConfig.json"))
        self.ser: serial.Serial | None = None
        self.module = "UNKNOWN"
        self.send_rate = self.config["DEFAULT_SEND_RATE"]
        self.tx_power = self.config["DEFAULT_TX_POWER"]
        self.connected = False
        self.tx_count = 0
        self.tx_fail = 0
        self.consecutive_errors = 0

    def connect(self, port: str, baud: int) -> bool:
        try:
            self.ser = serial.Serial(port, baud, timeout=self.config.get("SERIAL_TIMEOUT_S", 0.1))
            time.sleep(1.5)
            self.ser.reset_input_buffer()
            self.connected = True
            self.consecutive_errors = 0
            return True
        except Exception:
            self.connected = False
            return False

    def send_command(self, cmd: str) -> str | None:
        if not self.ser:
            return None
        try:
            self.ser.reset_input_buffer()
            self.ser.write((cmd + "\n").encode())
            time.sleep(0.15)
            resp = self.ser.readline().decode(errors="replace").strip() or None
            self.consecutive_errors = 0
            return resp
        except Exception:
            self.consecutive_errors += 1
            return None

    def handshake(self) -> bool:
        for _ in range(3):
            resp = self.send_command("HANDSHAKE")
            if resp and resp.startswith("ACK"):
                self._parse_status(resp.split())
                return True
            time.sleep(0.2)
        return False

    def _parse_status(self, parts: list[str]):
        if len(parts) >= 2:
            self.module = parts[1]
        if len(parts) >= 3:
            self.send_rate = int(parts[2])
        if len(parts) >= 4:
            self.tx_power = int(parts[3])

    def send_data(self, steer: int, accel: int, brake: bool, speed_sel: int, reverse: bool, commands: int):
        if not self.ser:
            self.tx_fail += 1
            self.consecutive_errors += 1
            return

        misc = ((speed_sel & 0x0F) << 4) | ((1 if brake else 0) << 3) | ((1 if reverse else 0) << 2) | (commands & 0x03)
        payload = struct.pack("BBB", steer, accel, misc)
        crc = crc16_ccitt(payload)
        frame = struct.pack("B", self.config["BINARY_MARKER"]) + payload + struct.pack(">H", crc)

        try:
            self.ser.write(frame)
            self.ser.flush()
            self.tx_count += 1
            self.consecutive_errors = 0
        except Exception:
            self.tx_fail += 1
            self.consecutive_errors += 1

    def poll_messages(self):
        msgs = []
        while self.ser and self.ser.in_waiting:
            line = self.ser.readline().decode(errors="replace").strip()
            if line:
                msgs.append(line)
        return msgs

    def has_serial_fault(self) -> bool:
        return self.consecutive_errors >= self.config.get("MAX_SERIAL_ERRORS", 8)

    def close(self):
        if self.ser:
            self.ser.close()
