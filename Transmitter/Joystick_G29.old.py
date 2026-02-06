import os
import pygame
import serial
import time

# Disabilita l'audio di Pygame
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Inizializza Pygame
pygame.init()
pygame.joystick.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Controllo con G29")

# Inizializza joystick (volante G29)
if pygame.joystick.get_count() == 0:
    print("Errore: nessun joystick trovato!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick rilevato: {joystick.get_name()}")

# Configura la porta seriale ESP32
try:
    ser = serial.Serial("COM3", 115200, timeout=1)
    time.sleep(2)
except serial.SerialException:
    print("Errore: impossibile aprire la porta seriale!")
    exit()

def normalizza_valore_motore(valore, min_in, max_in, min_out, max_out):
    """Mappa un valore da un intervallo a un altro."""
    return int((valore - min_in) / (max_in - min_in) * (max_out - min_out) + min_out)

def normalizza_valore(valore, min_in, max_in, min_out, max_out):
    # Mappatura inversa
    return int((max_in - valore) / (max_in - min_in) * (max_out - min_out) + min_out)


# Variabili per il motore (graduale)
motore_attuale = 127
incremento = 5

# Variabili per accelerazione e retromarcia
acceleratore = 0
retromarcia = 0

try:
    while True:
        pygame.event.pump()

        # Lettura assi
        sterzo_raw = joystick.get_axis(0)
        accel_raw = joystick.get_axis(1)
        freno_raw = joystick.get_axis(2)
        retro_raw = joystick.get_axis(3)

        # Calcolo angolo reale del volante (da -90° a +90°)
        angolo_volante = -sterzo_raw * 90

        # Mappatura angolo volante (-90° → 0, 0° → 15, +90° → 30)
        #è possibile l'ultimo valore della formula, ora è stato forzato a 90 ma orininariamente era 30
        #sterzo_servo= normalizza_valore(angolo_volante, -90, 90, 30, 120)
        #questo è il valore di
        sterzo_servo = normalizza_valore(angolo_volante, -90, 90, 130, 50)
        #sterzo_servo = normalizza_valore(angolo_volante, -90, 90, 130, 50)
        #sterzo_servo = normalizza_valore(angolo_volante, -90, 90, 102, 44)


        # Accelerazione progressiva
        if accel_raw < 0:
            acceleratore = min(acceleratore + 20, 240)
        elif accel_raw > 0:
            acceleratore = max(acceleratore - 5, 0)

        # Retromarcia progressiva
        if retro_raw < -0.1:
            retromarcia = max(retromarcia - 20, -240)
        else:
            retromarcia = min(retromarcia + 5, 0)

        # Mappatura motore
        if freno_raw < -0.1:
            target_motore = 127
        elif retro_raw < -0.1:
            target_motore = normalizza_valore_motore(-retro_raw, 0, 1, -240, -127)
        elif accel_raw < 0.1:
            target_motore = normalizza_valore_motore(-accel_raw, 0, 1, 127, 240)
        else:
            target_motore = 127

        # Priorità alla retromarcia
        if retro_raw < -0.1:
            target_motore = retromarcia

        # Transizione graduale
        if target_motore > motore_attuale:
            motore_attuale = min(motore_attuale + incremento, target_motore)
        elif target_motore < motore_attuale:
            motore_attuale = max(motore_attuale - incremento, target_motore)

        # Invio dati
        dati = f"{sterzo_servo},{motore_attuale}\n"
        if ser.is_open:
            ser.write(dati.encode())
            ser.flush()

        print(f"Angolo volante: {angolo_volante:.1f}°, Servo: {sterzo_servo}, Motore: {motore_attuale}")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nInterruzione: chiusura del programma...")
finally:
    ser.close()
    joystick.quit()
    pygame.quit()
