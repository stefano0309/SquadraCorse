import sys
from radio_controller import RadioController

def _bar(val: float, width: int = 20) -> str:
    """Return an ASCII bar like [████░░░░░░] for a 0-1 value."""
    filled = int(max(0.0, min(1.0, val)) * width)
    return '[' + '█' * filled + '░' * (width - filled) + ']'

# ══════════════ DISPLAY ══════════════
def display(rc: RadioController, steer_deg: float, servo_offset: float, steering_max: float,
            accel: float, brake: float,
            speed_sel: int, reverse: bool, actual_rate: float, log_lines: list, max_speeds: int):
    mod_str = {
        "LORA": f"LoRa 433 MHz  |  TX Power: {rc.tx_power} dBm",
        "NRF24": "nRF24L01+ 2.4 GHz",
        "NONE": "** NESSUN MODULO RILEVATO **"
    }.get(rc.module, rc.module)

    W = 60
    sep = "=" * W
    mid = "-" * W
    def pad(s): return s.ljust(W)

    tail = log_lines[-4:]
    conn_str = "CONNESSA" if rc.connected else "NON CONNESSA"
    lines = [
        "\033[H", sep,
        pad("       TRASMISSIONE SQUADRA CORSE"), sep,
        pad(f"  Modulo     : {mod_str}"),
        pad(f"  Seriale    : {conn_str}"),
        pad(f"  Frequenza  : {actual_rate:.0f} / {rc.send_rate} Hz"),
        pad(f"  Pacchetti  : {rc.tx_count}  errori: {rc.tx_fail}"), mid,
        pad(f"  Sterzo     : {steer_deg:+6.1f}°  (offset {servo_offset:+.1f}°)"),
        pad(f"  Potenza    : {_bar(accel, 20)} {accel * 100:5.1f}%"),
        pad(f"  Freno      : {_bar(brake, 20)} {brake * 100:5.1f}%"),
        pad(f"  Vel. Max   : {(1 + speed_sel) * 10}%  [{'RETRO' if reverse else 'AVANTI'}]"), mid,
    ]
    for i in range(4):
        lines.append(pad(f"  >> {tail[i]}") if i < len(tail) else pad(""))
    lines.extend([sep, pad("  [MENU] per impostazioni  |  CTRL+C per uscire")])
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()