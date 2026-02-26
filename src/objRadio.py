import serial
from src.utils import *

class RadioController:
    def __init__(self):
        self.config = readfile(os.getcwd()+"/src/data/radioConfig.json")
        self.ser: serial.Serial | None = None
        self.module = "UNKNOWN"
        self.send_rate = self.config['DEFAULT_SEND_RATE']
        self.tx_power = self.config['DEFAULT_TX_POWER']
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
        payload = struct.pack("BBB", steer, accel, misc)
        crc = crc16_ccitt(payload)
        
        frame = struct.pack("B", self.config['BINARY_MARKER']) + payload + struct.pack(">H", crc)
        
        try:
            self.ser.write(frame)
            self.ser.flush() 
            self.tx_count += 1
        except: 
            self.tx_fail += 1

    def poll_messages(self):
        msgs = []
        while self.ser and self.ser.in_waiting:
            line = self.ser.readline().decode(errors="replace").strip()
            if line: msgs.append(line)
        return msgs

    def close(self):
        if self.ser: self.ser.close()