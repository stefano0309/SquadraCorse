import sys
from radio_controller import RadioController

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
        pad(f"  Acceleraz. : {accel:6.2f}"),
        pad(f"  Freno      : {brake:6.2f}"),
        pad(f"  Vel. Max   : {(1 + speed_sel) * 10}%  [{'RETRO' if reverse else 'AVANTI'}]"), mid,
    ]
    for i in range(4):
        lines.append(pad(f"  >> {tail[i]}") if i < len(tail) else pad(""))
    lines.extend([sep, pad("  [MENU] per impostazioni  |  CTRL+C per uscire")])
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()