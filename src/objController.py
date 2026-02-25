import pygame
import argparse
import sys
import time
from colorama import *
from src.utils import *
from src.objRadio import RadioController

init(autoreset=True)

# Definizioni costanti per mappatura e menu
button_list = ["START", "EXIT", "SETTINGS", "UP", "DOWN", "SELECT", "RETRO_ON", "RETRO_OFF"]
axis_list = ["STEERING", "ACCELERATOR", "BRAKE"]
options_list = ["Regolazione massima velocità", 
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

        # --- Caricamento Workspace e Preset ---
        PATHS, BUTTON_PRESET, AXIS_PRESET = loadWorkSpace()
        # Carica velocity (0-100%) e angle (gradi) dal file presetIndex/presetPath
        self.velocity, self.angle = presetMenu(PATHS["presetIndex"], PATHS["presetPath"])
        
        self.paths = PATHS
        self.presetButton = BUTTON_PRESET
        self.presetAxis = AXIS_PRESET

        self.config = readfile(os.getcwd()+"\\src\\data\\radioConfig.json")

        self.rc = RadioController()
        parser = argparse.ArgumentParser()
        parser.add_argument("port", nargs="?", default="COM13" if sys.platform == "win32" else "/dev/ttyUSB0")
        args = parser.parse_args()

        self.rc.connect(args.port, self.config['SERIAL_BAUD'])
        self.rc.handshake()

        # --- Configurazione Mappatura Hardware ---
        #buttonMap(self.presetButton, self.presetAxis, button_list, axis_list, self.paths["configPath"])
        setUpVolante(self.js, button_list, axis_list, self.paths["configPath"])
        
        buttonMp, axisMp = loadMap(self.paths["configPath"])
        CLEAR()
        INIZIALISE(self.js)
        
        self.buttons = buttonMp
        self.axis = axisMp

        # --- Stato Interno ---
        self.running = True
        self.firstStart = True
        self.start = False
        self.settings = False
        self.selectItem = False
        self.retromarcia = False
        self.selected = 0
        self.position = 0
        self.option_selected = options_list
        
        # SOGLIA DRIFT (Deadzone)
        self.deadzone = 0.08  # Ignora input inferiori all'8%

    def apply_deadzone(self, value):
        """Applica zona morta e riscala l'input per fluidità."""
        if abs(value) < self.deadzone:
            return 0.0
        # Riscalatura: trasforma [deadzone, 1.0] in [0.0, 1.0]
        return (value - (self.deadzone if value > 0 else -self.deadzone)) / (1.0 - self.deadzone)

    def run(self):
        """Loop principale dell'applicazione."""
        while self.running:
            for event in pygame.event.get():
                self.gestioneUscite(event)
                self.gestioneBottoni(event)
                self.gestioneAssi(event)
            
            # Invio dati binari se il sistema è attivo
            if self.start and not self.settings:
                self.invioDati()
                time.sleep(0.02) 
                    
        if self.ser: 
            self.ser.close()
        pygame.quit()

    def invioDati(self):
        
        raw_steer = self.js.get_axis(self.axis["STEERING"])
        raw_accel = self.js.get_axis(self.axis["ACCELERATOR"])
        raw_brake = self.js.get_axis(self.axis["BRAKE"])
        
        # 2. Mappatura a 0-255
        # Lo sterzo ha centro a 0, va mappato con centro a 128
        steer_byte = int((raw_steer + 1.0) / 2.0 * 255)
        
        # Anche i grilletti (spesso) vanno da -1.0 (rilasciato) a 1.0 (premuto a fondo)
        accel_byte = int((raw_accel + 1.0) / 2.0 * 255)
        brake_byte = int((raw_brake + 1.0) / 2.0 * 255)
        
        # 3. Sicurezza: Forziamo i valori tra 0 e 255 (Clamp)
        steer_byte = max(0, min(255, steer_byte))
        accel_byte = max(0, min(255, accel_byte))
        brake_byte = max(0, min(255, brake_byte))
        
        # 4. Freno logico: applichiamo una deadzone (es. scatta solo se premuto oltre il 10%)
        is_braking = brake_byte > 25 
        
        # 5. Trasmissione
        self.rc.send_data(steer_byte, accel_byte, is_braking, self.velocity, self.retromarcia, 0)
        
        # Attesa per non saturare il modulo radio
        time.sleep(0.01)

    # --- Gestione Eventi ---
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
            print(Fore.CYAN + "RETROMARCIA: ON" + Style.RESET_ALL)
            
        elif event.button == self.buttons["RETRO_OFF"]:
            self.retromarcia = False
            print(Fore.CYAN + "RETROMARCIA: OFF" + Style.RESET_ALL)

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

        # Navigazione menu impostazioni tramite assi
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
            setUpVolante(self.js, button_list, axis_list, self.paths["configPath"])
            self.buttons, self.axis = loadMap(self.paths["configPath"])
            self.settings = False
            drawMenu()
        elif self.selected == 3: # Salva Preset
            presetMenu(self.paths["presetIndex"], self.paths["presetPath"], self.velocity, self.angle)
            self.selectItem = False
            drawSettings(self.selected, self.option_selected)
        else:
            drawSettings(self.selected, self.option_selected)
            if self.selected == 0: drawSettingOption(0, 100, self.velocity, 5)
            if self.selected == 1: drawSettingOption(0, 180, self.angle, 9)