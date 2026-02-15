import pathlib
import json

# ══════════════ CONFIGURAZIONE ══════════════
SERIAL_BAUD = 115200
DEFAULT_SEND_RATE = 20
MAX_SPEEDS = 6
BINARY_MARKER = 0xAA
MAPPING_FILE = pathlib.Path(__file__).parent / "mapping.json"
DISPLAY_REFRESH_S = 0.05