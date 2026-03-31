import pygame
import time
import sys
import signal
import argparse
import json
import pathlib

with open(pathlib.Path(__file__).parent / "config.json") as f:
    config = json.load(f)


# ══════════════ CARICAMENTO CONFIGURAZIONE ══════════════
#  Per aggiornare questi parametri modificare config.json

# Connessione Seriale al Trasmettitore
TX_PORT_WINDOWS = config['TX_PORT_WINDOWS'] # Porta Utilizata in caso di Sistema Windows
TX_PORT_LINUX = config['TX_PORT_LINUX'] # Porta Utilizzata in caso di Sistema Linux
SERIAL_BAUD = config['SERIAL_BAUD'] # Velocità della Comunicazione

# Parametri Guida
MAX_SPEEDS = config['MAX_SPEEDS'] # Numero massimo di velocità scalabili (da 1 a 16)
SERVO_ZERO_OFFSET = config.get('SERVO_ZERO_OFFSET', 0) # Definisce l'offset necessario per calibrare il servo
STEERING_MAX_ANGLE = config.get('STEERING_MAX_ANGLE', 90) # Definisce l'angolo massimo di rotazione del volante
WHEEL_RANGE_DEGREES = config.get('WHEEL_RANGE_DEGREES', 450) # Definisce l'angolo massimo di rotazione del servo

# Opzioni display
DISPLAY_REFRESH_S = config['DISPLAY_REFRESH_S'] # Definisce quante volte al secondo ricaricare lo schermo



# ══════════════ Importazione moduli esterni ══════════════
from utils import clear_once, get_axis_idx, get_axis_calibration, norm_pedal, norm_steer # Funzioni per la lettura degli assi
from mapping import load_mapping, save_mapping # Funzioni per caricare e salvare la mappatura
from radio_controller import RadioController # Classe per l'invio dei dati al TX
from controller_discovery import scopri_assi, scopri_pulsanti # Funzioni mappare la mappatura
from display import display # Funzione per implementare l'interfaccia grafica
from menu import run_menu # Funzione che apre il menù delle impostazioni
from pygame_init import init_pygame

# ══════════════ MAIN ══════════════
_quit_flag = False

def _sigint_handler(signum, frame):
    global _quit_flag
    _quit_flag = True

def main():
    global _quit_flag

    # Imposta la porta seriale
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs="?", default=TX_PORT_LINUX if sys.platform != "win32" else TX_PORT_WINDOWS)
    args = parser.parse_args()

    # Inizializza pygame
    init_pygame()
    signal.signal(signal.SIGINT, _sigint_handler)

    # Se non c'è nessun controller/volante collegato esce
    if pygame.joystick.get_count() == 0:
        print("  Nessun controller trovato!")
        return
    js = pygame.joystick.Joystick(0)

    # ══════════════ Mappatura ══════════════
    mapping = load_mapping() # Carica la mappatura precedente da mapping.json
    need_remap = True # Inizia presumendo che sia necessario rimappare

    if mapping and mapping.get("controller"):
            file_ctrl = mapping.get("controller") # Ottiene il nome del controller/volante utilizzato la scorsa volta
            js_ctrl = js.get_name() # Ottiene il nome del controller/volante collegato
            file_ctrl_norm = file_ctrl.lower().strip() # Normalizza il nome del controller precedentemente mappato
            js_ctrl_norm = js_ctrl.lower().strip() # Normalizza il nome del controller collegato

            # Verifica che il controller utilizzato precedentemente non sia cambiato
            same = (file_ctrl_norm == js_ctrl_norm or file_ctrl_norm in js_ctrl_norm or js_ctrl_norm in file_ctrl_norm)
            
            # Se il controller non è cambiato chiede conferma all'utente e carica la mappatura precedente
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
                    need_remap = False  # Se la mappatura viene confermata non è necessario rifarla (skippa lo step dopo)
                    print("  Mappatura confermata.")
                else:
                    print("  Rimappatura...")   
    
    # Se è necessario rimappare chiama la funzione apposita in mapping.py
    if need_remap:
        assi = scopri_assi(js)
        pulsanti = scopri_pulsanti(js)
        mapping = {"controller": js.get_name(), "assi": assi, "pulsanti": pulsanti}
        save_mapping(mapping)
        print("  Mappatura salvata in mapping.json")

    # Attende che tutti i pulsanti vengano rilasciati
    t0 = time.time()
    while time.time() - t0 < 1.0:
        pygame.event.pump()
        if not any(js.get_button(i) for i in range(js.get_numbuttons())):
            break
        time.sleep(0.02)

    assi = mapping["assi"]
    pulsanti = mapping["pulsanti"]
    if "STERZO" not in assi:
        print("\n  ERRORE: asse sterzo non mappato.")
        return
    if "ACCELERATORE" not in assi:
        print("\n  ERRORE: asse accelleratore non mappato.")
        return
    if "FRENO" not in assi:
        print("\n  ERRORE: asse freno non mappato.")
        return



    # ══════════════ Connessione al Trasmettitore ══════════════
    rc = RadioController()
    print(f"\n  Connessione a {args.port} ...")
    
    # Se il trasmettitore è collegato avvia fa un handshake, altrimenti va in sola visualizzazione
    if rc.connect(args.port, SERIAL_BAUD) and rc.handshake():
        print(f"  Handshake OK → modulo: {rc.module}") 
    else:
        print("  Seriale non disponibile – solo visualizzazione.")

    # Stato
    max_speeds = MAX_SPEEDS
    speed_sel = 0  # Velocità attualmente selezionata (in range tra 1 e MAX_SPEEDS)
    reverse = False # Retro abilitata, vero o falso
    commands = 0
    log_lines: list[str] = []

    # dizionario Configuration: contiene stato hardware, parametri, calibrazione e connessione
    cfg = {"send_rate": rc.send_rate, "max_speeds": max_speeds, "serial_port": args.port,
           "SERVO_ZERO_OFFSET": SERVO_ZERO_OFFSET, "STEERING_MAX_ANGLE": STEERING_MAX_ANGLE,
           "WHEEL_RANGE_DEGREES": WHEEL_RANGE_DEGREES}

    intervallo = 1.0 / max(1, rc.send_rate)
    ultimo_invio = 0.0
    rate_counter = 0
    rate_timer = time.time()
    actual_rate = 0.0
    last_display = 0.0

    # Parametri servo (copie locali mutabili, aggiornate dal menu)
    servo_zero_offset = SERVO_ZERO_OFFSET
    steering_max_angle = STEERING_MAX_ANGLE
    wheel_range_degrees = WHEEL_RANGE_DEGREES

    # soglia pressione per eseguire azioni al rilascio
    press_threshold = 0.02
    hold_start_main: dict[int, float] = {}

    clear_once()
    sys.stdout.write("\033[?25l")


    
    try:
        while not _quit_flag:
            pygame.event.pump()

            # Pulsanti: registra DOWN e attiva azione al rilascio (durata minima), bho sta roba è mistica ma funziona
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
                                if nome == "VEL_SU":
                                    speed_sel = min(max_speeds - 1, speed_sel + 1)
                                    log_lines.append(f"Vel. max → {(speed_sel + 1) * 10}%")
                                elif nome == "VEL_GIU":
                                    speed_sel = max(0, speed_sel - 1)
                                    log_lines.append(f"Vel. max → {(speed_sel + 1) * 10}%")
                                elif nome == "RETRO":
                                    reverse = not reverse
                                    log_lines.append(f"Retro {'ON' if reverse else 'OFF'}")
                                elif nome == "MENU":
                                    cfg = run_menu(js, pulsanti, assi, rc, cfg)
                                    if cfg.pop("_quit", False):
                                        _quit_flag = True
                                        break
                                    max_speeds = cfg.get("max_speeds", MAX_SPEEDS)
                                    speed_sel = min(speed_sel, max_speeds - 1)
                                    intervallo = 1.0 / max(1, rc.send_rate)
                                    # Aggiorna parametri servo dal cfg (possono essere cambiati nel menu)
                                    servo_zero_offset = cfg.get("SERVO_ZERO_OFFSET", SERVO_ZERO_OFFSET)
                                    steering_max_angle = cfg.get("STEERING_MAX_ANGLE", STEERING_MAX_ANGLE)
                                    wheel_range_degrees = cfg.get("WHEEL_RANGE_DEGREES", WHEEL_RANGE_DEGREES)
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


                # Lettura valori grezzi degli assi
                volante_raw = js.get_axis(get_axis_idx(assi, "STERZO"))
                accel_raw = js.get_axis(get_axis_idx(assi, "ACCELERATORE"))
                freno_raw = js.get_axis(get_axis_idx(assi, "FRENO"))

                # Normalizzazione con calibrazione rest/peak
                s_rest, s_peak = get_axis_calibration(assi, "STERZO")
                a_rest, a_peak = get_axis_calibration(assi, "ACCELERATORE")
                f_rest, f_peak = get_axis_calibration(assi, "FRENO")

                volante = norm_steer(volante_raw, s_rest, s_peak)
                accel_norm = norm_pedal(accel_raw, a_rest, a_peak)
                freno_norm = norm_pedal(freno_raw, f_rest, f_peak)

                # Sterzo: zona morta + curva esponenziale per amplificare l'errore
                STEER_DEADZONE = 0.01          # sotto l'1% → centro esatto
                STEER_EXPO     = 2.5           # esponente: >1 = più aggressivo fuori dalla zona morta
                if abs(volante) < STEER_DEADZONE:
                    volante = 0.0
                else:
                    sign = 1.0 if volante > 0 else -1.0
                    # Remap [deadzone..1] → [0..1], poi curva potenza
                    remapped = (abs(volante) - STEER_DEADZONE) / (1.0 - STEER_DEADZONE)
                    volante = sign * (remapped ** STEER_EXPO)

                # Freno: soglia 10% per attivazione
                brake_pressed = freno_norm > 0.10

                # Se il freno è premuto, l'accelleratore va a 0
                if brake_pressed:
                    accel_norm = 0.0

                accel_byte = int(accel_norm * 255)

                # Conversione sterzo: asse → gradi → clamp a ±STEERING_MAX → applica offset → byte
                wheel_deg = volante * (wheel_range_degrees / 2)
                steer_deg = max(-steering_max_angle, min(steering_max_angle, wheel_deg))
                output_deg = steer_deg + servo_zero_offset
                # Inversione sterzo
                steer_byte = int(((-output_deg + steering_max_angle) / (2 * steering_max_angle)) * 255)
                steer_byte = max(0, min(255, steer_byte))

                if rc.connected:
                    rc.send_data(steer_byte, accel_byte, brake_pressed, speed_sel, reverse, commands)

            # Display
            if now - last_display >= DISPLAY_REFRESH_S:
                last_display = now
                display(rc, steer_deg, servo_zero_offset, steering_max_angle,
                        accel_norm, freno_norm,
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
