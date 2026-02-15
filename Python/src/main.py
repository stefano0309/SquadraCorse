import pygame
import time
import sys
import argparse

from config import SERIAL_BAUD, MAX_SPEEDS, DISPLAY_REFRESH_S
from utils import clear_once
from mapping import load_mapping, save_mapping
from radio_controller import RadioController
from controller_discovery import scopri_assi, scopri_pulsanti
from display import display
from menu import run_menu
from pygame_init import init_pygame

# ══════════════ MAIN ══════════════
def main():
    parser = argparse.ArgumentParser(description="TX Squadra Corse – solo terminale")
    parser.add_argument("port", nargs="?", default="/dev/ttyUSB0" if sys.platform != "win32" else "COM9")
    args = parser.parse_args()

    init_pygame()
    if pygame.joystick.get_count() == 0:
        print("  Nessun controller trovato!")
        return
    js = pygame.joystick.Joystick(0)

    # Mapping
    mapping = load_mapping()
    need_remap = True
    if mapping and mapping.get("controller"):
        file_ctrl = mapping.get("controller")
        js_ctrl = js.get_name()
        file_ctrl_norm = file_ctrl.lower().strip()
        js_ctrl_norm = js_ctrl.lower().strip()
        same = (file_ctrl_norm == js_ctrl_norm or file_ctrl_norm in js_ctrl_norm or js_ctrl_norm in file_ctrl_norm)
        if same:
            print(f"\n  Mappatura trovata per controller: {file_ctrl}")
            print("  Premi un pulsante qualsiasi per confermare o attendi 5 s per rimappare...")
            deadline = time.time() + 5
            confermato = False
            while time.time() < deadline:
                for ev in pygame.event.get():
                    if ev.type == pygame.JOYBUTTONDOWN:
                        confermato = True
                        break
                if confermato:
                    break
                # anche polling sui pulsanti (nel caso non ci siano eventi)
                if any(js.get_button(i) for i in range(js.get_numbuttons())):
                    confermato = True
                    break
                time.sleep(0.02)
            if confermato:
                need_remap = False
                print("  Mappatura confermata.")
            else:
                print("  Rimappatura...")
        else:
            print(f"\n  Mappatura presente in mapping.json per '{file_ctrl}', ma controller connesso è '{js_ctrl}'. Rimappatura forzata.")

    if need_remap:
        assi = scopri_assi(js)
        pulsanti = scopri_pulsanti(js)
        mapping = {"controller": js.get_name(), "assi": assi, "pulsanti": pulsanti}
        save_mapping(mapping)
        print("  Mappatura salvata in mapping.json")

    assi = mapping["assi"]
    pulsanti = mapping["pulsanti"]
    if "STERZO" not in assi:
        print("\n  ERRORE: asse sterzo non mappato.")
        return

    # Connessione
    rc = RadioController()
    print(f"\n  Connessione a {args.port} ...")
    if rc.connect(args.port, SERIAL_BAUD) and rc.handshake():
        print(f"  Handshake OK → modulo: {rc.module}")
    else:
        print("  Seriale non disponibile – solo visualizzazione.")

    # Stato
    max_speeds = MAX_SPEEDS
    speed_sel = 0
    reverse = False
    commands = 0
    log_lines: list[str] = []
    cfg = {"tx_power": rc.tx_power, "send_rate": rc.send_rate, "max_speeds": max_speeds, "serial_port": args.port}

    intervallo = 1.0 / max(1, rc.send_rate)
    ultimo_invio = 0.0
    rate_counter = 0
    rate_timer = time.time()
    actual_rate = 0.0
    last_display = 0.0

    # soglia pressione per eseguire azioni al rilascio
    press_threshold = 0.08
    hold_start_main: dict[int, float] = {}

    clear_once()
    sys.stdout.write("\033[?25l")

    # inizializza valori assi per evitare variabili non definite nel display
    volante = 0.0
    accel = -1.0
    freno = -1.0

    try:
        while True:
            pygame.event.pump()

            # Pulsanti: registra DOWN e attiva azione al rilascio (durata minima)
            for ev in pygame.event.get():
                if ev.type == pygame.JOYBUTTONDOWN:
                    for nome, idx in pulsanti.items():
                        if ev.button == idx:
                            hold_start_main[idx] = time.time()
                            break
                elif ev.type == pygame.JOYBUTTONUP:
                    for nome, idx in pulsanti.items():
                        if ev.button == idx:
                            start = hold_start_main.pop(idx, None)
                            if start is not None and time.time() - start >= press_threshold:
                                if nome == "MARCIA_SU":
                                    speed_sel = min(max_speeds - 1, speed_sel + 1)
                                    log_lines.append(f"Marcia → {speed_sel + 1}")
                                elif nome == "MARCIA_GIU":
                                    speed_sel = max(0, speed_sel - 1)
                                    log_lines.append(f"Marcia → {speed_sel + 1}")
                                elif nome == "RETRO":
                                    reverse = not reverse
                                    log_lines.append("RETRO ON" if reverse else "RETRO OFF")
                                elif nome == "MENU":
                                    cfg = run_menu(js, pulsanti, rc, cfg)
                                    max_speeds = cfg.get("max_speeds", MAX_SPEEDS)
                                    speed_sel = min(speed_sel, max_speeds - 1)
                                    intervallo = 1.0 / max(1, rc.send_rate)
                                    log_lines.append("Menu chiuso")
                                    if cfg.pop("_need_remap", False):
                                        assi = scopri_assi(js)
                                        pulsanti = scopri_pulsanti(js)
                                        mapping = {"controller": js.get_name(), "assi": assi, "pulsanti": pulsanti}
                                        save_mapping(mapping)
                                        log_lines.append("Rimappatura completata")
                                    clear_once()
                            break

            # Messaggi TX
            if rc.connected:
                for m in rc.poll_messages():
                    if m.startswith("MODULE_CHANGED"):
                        log_lines.append(f"Modulo cambiato → {rc.module}")
                        rc.handshake()
                        intervallo = 1.0 / max(1, rc.send_rate)
                    elif "FAIL" in m or "ERR" in m:
                        log_lines.append(m)

            # Invio
            now = time.time()
            if now - ultimo_invio >= intervallo:
                ultimo_invio = now
                rate_counter += 1
                if now - rate_timer >= 1.0:
                    actual_rate = rate_counter
                    rate_counter = 0
                    rate_timer = now

                volante = js.get_axis(assi.get("STERZO", 0))
                accel = js.get_axis(assi.get("ACCELERATORE", 0))
                freno = js.get_axis(assi.get("FRENO", 0))

                steer_byte = max(0, min(255, int((volante + 1.0) * 127.5)))
                accel_byte = max(0, min(255, int((accel + 1.0) / 2 * 255)))
                brake_byte = max(0, min(255, int((freno + 1.0) / 2 * 255)))

                if rc.connected:
                    rc.send_data(steer_byte, accel_byte, brake_byte, speed_sel, reverse, commands)

            # Display
            if now - last_display >= DISPLAY_REFRESH_S:
                last_display = now
                display(rc, volante, (accel + 1) / 2, (freno + 1) / 2,
                        speed_sel, reverse, actual_rate, log_lines, max_speeds)
                if len(log_lines) > 50:
                    log_lines = log_lines[-20:]

            time.sleep(0.005)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h")
        print("\n\n  Chiusura …")
        rc.close()
        pygame.quit()


if __name__ == "__main__":
    main()
