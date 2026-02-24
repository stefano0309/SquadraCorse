import pygame
import json
import serial
import struct
from colorama import *
from src.utils import *

init(autoreset=True)

# Definizioni tasti e opzioni
button = ["START", "EXIT", "SETTINGS", "UP", "DOWN", "SELECT", "RETRO_ON", "RETRO_OFF"]
axis = ["STEERING", "ACCELERATOR", "BRAKE"]
option = ["Regolazione massima velocità", 
          "Regolazione angolo massimo sterzo", 
          "Reset mappatura tasti",
          "Salva preset impostazioni"]

class Controller():
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("Nessun controller trovato.")
            pygame.quit()
            quit()

        self.js = pygame.joystick.Joystick(0)
        self.js.init()

        # Configurazione Seriale
        try:
            # Assicurati che la porta COM corrisponda a quella del tuo trasmettitore
            self.ser = serial.Serial("COM9", 115200, timeout=0.1) 
            print(Fore.GREEN + "Connessione seriale stabilita." + Style.RESET_ALL)
        except Exception as e:
            self.ser = None
            print(Fore.RED + f"Errore seriale: {e}. Modalità simulazione attiva." + Style.RESET_ALL)

        # Caricamento ambiente e preset
        PATHS, BUTTON, AXIS = loadWorkSpace()
        self.velocity, self.angle = presetMenu(PATHS["presetIndex"], PATHS["presetPath"])
        
        self.paths = PATHS
        self.presetButton = BUTTON
        self.presetAxis = AXIS

        # Mappatura hardware
        buttonMap(self.presetButton, self.presetAxis, button, axis, self.paths["configPath"])
        setUpVolante(self.js, button, axis, self.paths["configPath"])
        
        buttonMp, axisMp = loadMap(self.paths["configPath"])
        CLEAR()

        INIZIALISE(self.js)
        
        # Stato veicolo e dati
        self.data = {}
        self.buttons = buttonMp
        self.axis = axisMp

        # Stato applicazione
        self.running = True
        self.firstStart = True
        self.start = False
        self.settings = False
        self.selectItem = False
        self.retromarcia = False
        
        # Gestione UI
        self.selected = 0
        self.position = 0
        self.option_selected = option

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.gestioneUscite(event)
                self.gestioneBottoni(event)
                self.gestioneAssi(event)
            
            # Invio continuo dei dati se il veicolo è avviato
            if self.start and not self.settings:
                self.invioDati()
                time.sleep(0.02) # Frequenza circa 50Hz
                    
        if self.ser: self.ser.close()
        pygame.quit()

    def gestioneUscite(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False

    def gestioneBottoni(self, event):
        if event.type != pygame.JOYBUTTONDOWN:
            return
        
        if event.button == self.buttons["RETRO_ON"]:
            self.retromarcia = True
            print(Fore.GREEN + "Retromarcia inserita." + Style.RESET_ALL)
            
        elif event.button == self.buttons["RETRO_OFF"]:
            self.retromarcia = False
            print(Fore.GREEN + "Retromarcia disinserita." + Style.RESET_ALL)

        elif event.button == self.buttons["START"]:
            self.gestioneInizio()
        
        elif event.button == self.buttons["EXIT"]:
            self.gestioneUsciteBottoni()

        if self.settings:
            self.gestioneBottoniImpostazioni(event)
        elif event.button == self.buttons["SETTINGS"] and not self.start:
            self.gestioneImpostazioni()
    
    def gestioneAssi(self, event):
        if event.type != pygame.JOYAXISMOTION:
            return

        # Navigazione impostazioni tramite asse (es. sterzo)
        if self.settings and self.selectItem:
            if self.selected == 0: # Velocità
                self.position, self.velocity = settingOption(event.value, self.position, 100, 0, self.velocity, self.selected, 0, 5, self.option_selected)
            elif self.selected == 1: # Angolo
                self.position, self.angle = settingOption(event.value, self.position, 180, 0, self.angle, self.selected, 1, 9, self.option_selected)

    def gestioneInizio(self):
        if self.firstStart:
            CLEAR()
            self.firstStart = False
            self.start = True
            drawMenu()
        else:
            self.start = not self.start
            drawMenu()
    
    def gestioneUsciteBottoni(self):
        if not self.start and not self.settings:
            self.running = False
        if self.settings:
            self.settings = False
            self.selectItem = False
            drawMenu()
            
    def gestioneImpostazioni(self):
        self.settings = True
        self.selected = 0
        drawSettings(self.selected, self.option_selected)
    
    def gestioneBottoniImpostazioni(self, event):
        if event.button == self.buttons["UP"]:
            self.selectItem = False
            self.selected = max(0, self.selected - 1)
            drawSettings(self.selected, self.option_selected)

        elif event.button == self.buttons["DOWN"]:
            self.selectItem = False
            self.selected = min(len(self.option_selected) - 1, self.selected + 1)
            drawSettings(self.selected, self.option_selected)

        elif event.button == self.buttons["SELECT"]:
            self.gestioneOpzioniImpostazioni()
    
    def gestioneOpzioniImpostazioni(self):
        if self.selectItem:
            self.selectItem = False
            drawSettings(self.selected, self.option_selected)
            return

        self.selectItem = True
        CLEAR()
        if self.selected == 2: # Reset Mappatura
            setUpVolante(self.js, button, axis, self.paths["configPath"])
            self.buttons, self.axis = loadMap(self.paths["configPath"])
            self.settings = False
            drawMenu()
        elif self.selected == 3: # Salva Preset
            presetMenu(self.paths["presetIndex"], self.paths["presetPath"], self.velocity, self.angle)
            self.selectItem = False
            drawSettings(self.selected, self.option_selected)
        else:
            # Visualizza barre di regolazione per Vel/Angolo
            drawSettings(self.selected, self.option_selected)
            if self.selected == 0: drawSettingOption(0, 100, self.velocity, 5)
            if self.selected == 1: drawSettingOption(0, 180, self.angle, 9)

    def invioDati(self):
        # 1. Lettura assi
        steer_raw = self.js.get_axis(self.axis["STEERING"])
        accel_raw = (self.js.get_axis(self.axis["ACCELERATOR"]) + 1) / 2 # Normalizzato 0-1
        brake_raw = (self.js.get_axis(self.axis["BRAKE"]) + 1) / 2       # Normalizzato 0-1

        # 2. Applicazione limiti dai preset (Percentuale velocità)
        # La velocità massima effettiva è limitata da self.velocity (0-100%)
        accel_limitato = accel_raw * (self.velocity / 100.0)
        
        # L'angolo sterzo è già gestito dal valore float -1 a 1, 
        # il ricevitore userà self.angle per mappare i gradi.
        
        # 3. Generazione pacchetto binario
        # Utilizziamo la marcia fissa a 0 poiché il sistema marce è rimosso
        pachetto = genera_pacchetto(
            steer_raw, 
            accel_limitato, 
            brake_raw, 
            0, # speed_sel rimosso
            self.retromarcia, 
            0
        )

        # 4. Invio seriale
        if self.ser and self.ser.is_open:
            self.ser.write(pachetto)