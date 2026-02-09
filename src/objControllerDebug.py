import pygame
import json
from colorama import *
from src.utils import *

init(autoreset=True)

path = "./config.json"

btns = ["START", "EXIT", "SETTINGS", "UP", "DOWN", "SELECT", "RETRO_ON", "RETRO_OFF"]
ax = ["STEERING", "ACCELERATOR", "BRAKE"]

class ControllerDebug():
    def __init__(self):
        pygame.init()
        # In modalità debug carichiamo la mappa o usiamo i preset
        # NOTA: Per il debug saltiamo la creazione fisica se il file non esiste
        if not os.path.exists(path):
            print("Configurazione non trovata. Uso mappatura tastiera standard.")
            # Mock dei dizionari per far funzionare i riferimenti self.buttons
            self.buttons = {b: i for i, b in enumerate(btns)}
            self.axis = {a: i for i, a in enumerate(ax)}
        else:
            self.buttons, self.axis = loadMap(path)

        INIZIALISE_DEBUG()

        # Dati Veicolo
        self.data = {"volante": 0.0, "acceleratore": -1.0, "freno": -1.0}
        self.velocity = 50
        self.angle = 45
        self.option_selected = ["Regolazione massima velocità", 
                                "Regolazione angolo massimo sterzo", 
                                "Reset mappatura tasti"]

        # Stato UI
        self.selected = 0
        self.position = 0 # Usato da settingOption
        self.running = True
        self.start = False
        self.settings = False
        self.selectItem = False
        self.retromarcia = False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    self.gestioneInput(event.key)
            
            if self.start:
                self.simulaDatiAssi()
                showInfo(self.data["volante"], self.data["acceleratore"], self.data["freno"])
                pygame.time.delay(50) # Riduce flickering in console

        pygame.quit()

    def gestioneInput(self, key):
        # Mappatura tasti di Debug
        K_START = pygame.K_s      # PS Button
        K_SETTINGS = pygame.K_p   # Quadrato
        K_EXIT = pygame.K_x       # X
        K_SELECT = pygame.K_RETURN # Cerchio
        K_UP = pygame.K_UP
        K_DOWN = pygame.K_DOWN
        K_LEFT = pygame.K_LEFT    # Simula asse negativo
        K_RIGHT = pygame.K_RIGHT  # Simula asse positivo

        # Gestione START/STOP
        if key == K_START:
            self.start = not self.start
            drawMenu()

        # Gestione EXIT
        if key == K_EXIT:
            if self.settings:
                self.settings = False
                self.selectItem = False
                drawMenu()
            else:
                print(Fore.RED + "Uscita..." + Style.RESET_ALL)
                self.running = False

        # Gestione SETTINGS
        if key == K_SETTINGS and not self.start:
            self.settings = True
            self.selected = 0
            drawSettings(self.selected, self.option_selected)

        # Navigazione Menu
        if self.settings and not self.selectItem:
            if key == K_UP:
                self.selected = max(0, self.selected - 1)
                drawSettings(self.selected, self.option_selected)
            elif key == K_DOWN:
                self.selected = min(len(self.option_selected) - 1, self.selected + 1)
                drawSettings(self.selected, self.option_selected)
            elif key == K_SELECT:
                self.selectItem = True
                # Forza il disegno iniziale dell'opzione scelta
                drawSettings(self.selected, self.option_selected)
                print(Fore.GREEN + "MODIFICA ATTIVA (Frecce Sinistra/Destra)" + Style.RESET_ALL)

        # Modifica Valori (Usa la tua funzione settingOption)
        elif self.settings and self.selectItem:
            if key == K_SELECT: # Premere di nuovo per uscire dalla modifica
                self.selectItem = False
                drawSettings(self.selected, self.option_selected)
            
            # Simuliamo il valore dell'asse: Destra = 1.0, Sinistra = -1.0
            val_simulato = 0
            if key == K_RIGHT: val_simulato = 1.0
            if key == K_LEFT: val_simulato = -1.0

            if val_simulato != 0:
                if self.selected == 0:
                    self.position, self.velocity = settingOption(
                        val_simulato, self.position, 100, 0, self.velocity, 
                        self.selected, 0, 5, self.option_selected
                    )
                elif self.selected == 1:
                    self.position, self.angle = settingOption(
                        val_simulato, self.position, 180, 0, self.angle, 
                        self.selected, 1, 9, self.option_selected
                    )

    def simulaDatiAssi(self):
        """Usa WASD per simulare gli assi durante la marcia."""
        keys = pygame.key.get_pressed()
        
        # Volante (A/D)
        if keys[pygame.K_a]: self.data["volante"] = -1.0
        elif keys[pygame.K_d]: self.data["volante"] = 1.0
        else: self.data["volante"] = 0.0

        # Acceleratore (W) e Freno (S)
        self.data["acceleratore"] = 1.0 if keys[pygame.K_w] else -1.0
        self.data["freno"] = 1.0 if keys[pygame.K_s] else -1.0
