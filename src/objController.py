import pygame
import json
import serial
import struct
import time
from colorama import *
from src.utils import *

init(autoreset=True)

# Configurazione nomi tasti e assi (devono corrispondere a quelli in utils.py)
BUTTON_LIST = ["START", "EXIT", "SETTINGS", "UP", "DOWN", "SELECT", "RETRO_ON", "RETRO_OFF"]
AXIS_LIST = ["STEERING", "ACCELERATOR", "BRAKE"]
OPTIONS_LIST = ["Regolazione massima velocità", 
                "Regolazione angolo massimo sterzo", 
                "Reset mappatura tasti",
                "Salva preset impostazioni"]

class Controller():
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print(Fore.RED + "ERRORE: Nessun controller trovato." + Style.RESET_ALL)
            pygame.quit()
            quit()

        self.js = pygame.joystick.Joystick(0)
        self.js.init()

        # --- Connessione Seriale ---
        # Baudrate 115200 come richiesto da TxCompleto.ino
        try:
            self.ser = serial.Serial("COM9", 115200, timeout=0.1) 
            print(Fore.GREEN + "Trasmettitore connesso su COM9." + Style.RESET_ALL)
        except Exception as e:
            self.ser = None
            print(Fore.YELLOW + "AVVISO: Seriale non trovata. Modalità simulazione." + Style.RESET_ALL)

        # --- Inizializzazione Dati e Preset ---
        PATHS, BUTTON_PRESET, AXIS_PRESET = loadWorkSpace()
        self.velocity, self.angle = presetMenu(PATHS["presetIndex"], PATHS["presetPath"])
        
        self.paths = PATHS
        self.deadzone = 0.08 # Tolleranza per joystick drift (8%)
        
        # Configurazione mappatura joystick
        buttonMap(BUTTON_PRESET, AXIS_PRESET, BUTTON_LIST, AXIS_LIST, self.paths["configPath"])
        setUpVolante(self.js, BUTTON_LIST, AXIS_LIST, self.paths["configPath"])
        
        self.buttons, self.axis = loadMap(self.paths["configPath"])
        CLEAR()
        INIZIALISE(self.js)

        # Stati logici
        self.running = True
        self.start = False
        self.settings = False
        self.selectItem = False
        self.retromarcia = False
        self.selected = 0
        self.position = 0
        self.option_selected = OPTIONS_LIST

    def apply_deadzone(self, value):
        """Rimuove i piccoli segnali di errore quando l'asse è a riposo."""
        if abs(value) < self.deadzone:
            return 0.0
        return (value - (self.deadzone if value > 0 else -self.deadzone)) / (1.0 - self.deadzone)

    def run(self):
        """Loop principale: legge gli input e invia i dati al TX."""
        while self.running:
            for event in pygame.event.get():
                self.gestioneUscite(event)
                self.gestioneBottoni(event)
                self.gestioneAssi(event)
            
            # Invio dati solo se il veicolo è in stato 'START'
            if self.start and not self.settings:
                self.invioDati()
                # Frequenza di invio ~50Hz (20ms)
                time.sleep(0.02) 
                    
        if self.ser: self.ser.close()
        pygame.quit()

    def invioDati(self):
        """Genera e invia il frame binario di 6 byte per TxCompleto.ino"""
        # 1. Lettura assi e applicazione Deadzone
        steer_val = self.apply_deadzone(self.js.get_axis(self.axis["STEERING"]))
        
        # Normalizzazione pedali (da -1/+1 a 0.0/1.0)
        accel_raw = max(0.0, (self.js.get_axis(self.axis["ACCELERATOR"]) + 1) / 2)
        brake_raw = max(0.0, (self.js.get_axis(self.axis["BRAKE"]) + 1) / 2)

        # 2. Scaling Velocità in base al Preset (%)
        # Se velocity=50, accel_final sarà max 0.5
        accel_final = accel_raw * (self.velocity / 100.0)

        # 3. Conversione in valori per il protocollo (0-255)
        steer_byte = max(0, min(255, int((steer_val + 1) * 127.5)))
        accel_byte = max(0, min(255, int(accel_final * 255)))

        # 4. Costruzione Byte MISC (Mapping bit di TxCompleto.ino)
        # Formato: [0-3: Speed (0)] | [4: Brake] | [5: Reverse] | [6-7: Extra (0)]
        brake_bit = 1 if brake_raw > 0.1 else 0
        reverse_bit = 1 if self.retromarcia else 0
        
        # Marce rimosse (speed_sel = 0), quindi shiftiamo i bit 4 e 5
        misc_byte = (0 << 4) | (brake_bit << 3) | (reverse_bit << 2) | 0

        # 5. Calcolo CRC-16 CCITT
        # Il CRC viene calcolato sui 3 byte di dati: steer, accel, misc
        payload = struct.pack("BBB", steer_byte, accel_byte, misc_byte)
        checksum = crc16_ccitt(payload) 

        # 6. Composizione Frame Finale (6 byte)
        # 0xAA (Marker) | Steer | Accel | Misc | CRC_High | CRC_Low
        frame = struct.pack(">BBBBH", 0xAA, steer_byte, accel_byte, misc_byte, checksum)

        if self.ser and self.ser.is_open:
            self.ser.write(frame)

    # --- Gestione Eventi e Menu ---
    def gestioneUscite(self, event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.running = False

    def gestioneBottoni(self, event):
        if event.type != pygame.JOYBUTTONDOWN: return
        
        if event.button == self.buttons["RETRO_ON"]:
            self.retromarcia = True
            print(Fore.CYAN + "MODALITÀ: RETROMARCIA" + Style.RESET_ALL)
        elif event.button == self.buttons["RETRO_OFF"]:
            self.retromarcia = False
            print(Fore.CYAN + "MODALITÀ: AVANTI" + Style.RESET_ALL)
        elif event.button == self.buttons["START"]:
            self.start = not self.start
            CLEAR()
            drawMenu()
        elif event.button == self.buttons["EXIT"]:
            if self.settings:
                self.settings = False
                self.selectItem = False
                drawMenu()
            else:
                self.running = False

        if self.settings:
            self.gestioneBottoniImpostazioni(event)
        elif event.button == self.buttons["SETTINGS"] and not self.start:
            self.settings = True
            self.selected = 0
            drawSettings(self.selected, self.option_selected)

    def gestioneBottoniImpostazioni(self, event):
        if event.button == self.buttons["UP"]:
            self.selected = max(0, self.selected - 1)
            drawSettings(self.selected, self.option_selected)
        elif event.button == self.buttons["DOWN"]:
            self.selected = min(len(self.option_selected) - 1, self.selected + 1)
            drawSettings(self.selected, self.option_selected)
        elif event.button == self.buttons["SELECT"]:
            self.gestioneOpzioniImpostazioni()

    def gestioneOpzioniImpostazioni(self):
        if self.selected == 2: # Reset
            setUpVolante(self.js, BUTTON_LIST, AXIS_LIST, self.paths["configPath"])
            self.buttons, self.axis = loadMap(self.paths["configPath"])
            self.settings = False
            drawMenu()
        elif self.selected == 3: # Salva
            presetMenu(self.paths["presetIndex"], self.paths["presetPath"], self.velocity, self.angle)
            self.settings = False
            drawMenu()
        else:
            self.selectItem = not self.selectItem
            drawSettings(self.selected, self.option_selected)

    def gestioneAssi(self, event):
        if self.settings and self.selectItem:
            if self.selected == 0: # Max Speed
                self.position, self.velocity = settingOption(event.value, self.position, 100, 0, self.velocity, self.selected, 0, 5, self.option_selected)
            elif self.selected == 1: # Max Angle
                self.position, self.angle = settingOption(event.value, self.position, 180, 0, self.angle, self.selected, 1, 9, self.option_selected)