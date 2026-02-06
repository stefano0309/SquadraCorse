import pygame
import json
from colorama import *
from src.utils import *

init(autoreset=True)

path = "./config.json"
button = ["START", "EXIT", "SETTINGS", "UP", "DOWN", "SELECT", "RETRO_ON", "RETRO_OFF"]
axis = ["STEERING", "ACCELERATOR", "BRAKE"]
option = ["Regolazione massima velocità",
          "Regolazione angolo massimo sterzo",
          "Reset mappatura tasti"]

class Volante():
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("Nessun controller trovato.")
            pygame.quit()
            quit()

        self.js = pygame.joystick.Joystick(0)

        buttonMap(button, axis, path)
        buttonMp, axisMp = loadMap(path)

        INIZIALISE(self.js)

        #Dati
        self.data = {}
        self.dataSetting = {}

        #Stato veicolo
        self.velocity = 50
        self.angle = 45

        #inputs
        self.option_selected = option
        self.buttons = buttonMp
        self.axis = axisMp

        #Stato UI
        self.selected = 0
        self.position = 0

        #Stato appicazione
        self.running = True
        self.firstStart = True
        self.start = False
        self.settings = False
        self.selectItem = False
        self.retromarcia = False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.gestioneUscite(event)
                self.gestioneBottoni(event)
                self.gestioneAssi(event)

        pygame.quit()

    def gestioneUscite(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

    def gestioneBottoni(self, event):
        if event.type != pygame.JOYBUTTONDOWN:
            return

        print(f"Pulsante premuto: {event.button}")

        if event.button == self.buttons["RETRO_ON"]:
            self.retromarcia = True
            print(Fore.GREEN + "Retromarcia inserita." + Style.RESET_ALL)

        if event.button == self.buttons["RETRO_OFF"]:
            self.retromarcia = False
            print(Fore.GREEN + "Retromarcia disinserita." + Style.RESET_ALL)

        if event.button == self.buttons["START"]:
            self.gestioneInizio()

        if event.button == self.buttons["EXIT"]:
            self.gestioneUsciteBottoni()

        if not self.settings and event.button == self.buttons["SETTINGS"] and not self.start:
            self.gestioneImpostazioni()

        if self.settings:
            self.gestioneBottoniImpostazioni(event)

    def gestioneAssi(self, event):
        if event.type != pygame.JOYAXISMOTION:
            return

        if event.axis == self.axis["STEERING"] and self.selectItem:
            if self.selected == 0:
                self.position, self.velocity = settingOption(event.value, self.position, 100, 0, self.velocity, self.selected, 0, 5, self.option_selected)
            if self.selected == 1:
                self.position, self.angle = settingOption(event.value, self.position, 180, 0, self.angle, self.selected, 1, 9, self.option_selected)

        if self.start:
            self.invioDati()

    def gestioneInizio(self):
        if self.firstStart:
            CLEAR()
            self.firstStart = False
            print("Avvio del veicolo...")
            self.start == True
            drawMenu()

        elif not self.start:
            drawMenu()
            self.start = True

        else:
            self.start = False
            drawMenu()

    def gestioneUsciteBottoni(self):
        if not self.start and not self.settings:
            print(Fore.GREEN + "Exit selezionato. Uscita dal programma." + Style.RESET_ALL)
            self.running = False
        if self.settings:
            self.settings = False
            self.selectItem = False
            self.dataSetting.update({
                "velocity": self.velocity,
                "angle": self.angle
            })
            packet = json.dumps(self.dataSetting)
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

        if event.button == self.buttons["DOWN"]:
            self.selectItem = False
            self.selected = min(len(self.option_selected) - 1, self.selected + 1)
            drawSettings(self.selected, self.option_selected)

        if event.button == self.buttons["SELECT"]:
            self.gestioneOpzioniImpostazioni()

    def gestioneOpzioniImpostazioni(self):
        self.positionNow = 0

        if self.selectItem:
            self.selectItem = False
            drawSettings(self.selected, self.option_selected)
            return

        self.selectItem = True
        CLEAR()
        print("Impostazioni veicolo selezionate.")
        for idx, option in enumerate(self.option_selected, start=1):
            if idx - 1 == self.selected:
                print(Fore.YELLOW + f"\t> {idx}. {option} <")
                if self.selected == 0:
                    drawSettingOption(0, 100, self.velocity, 5)
                if self.selected == 1:
                    drawSettingOption(0, 180, self.angle, 9)
                if self.selected == 2:
                    CLEAR()
                    os.remove(path)
                    buttonMap(button, axis, path)
                    self.buttons, self.axis = loadMap(path)
                    CLEAR()
                    self.settings = False
                    drawMenu()

            else:
                print(f"\t{idx}. {option}")
        if self.settings:
            print("Premi CERCHIO per selezionare l'opzione.")
            print(Fore.RED + "Premi X per tornare al menu principale.")

    def invioDati(self):
        self.data.update({
            "volante": round(self.js.get_axis(self.axis["STEERING"]), 2),
            "acceleratore": round(self.js.get_axis(self.axis["ACCELERATOR"]), 2),
            "freno": round(self.js.get_axis(self.axis["BRAKE"]), 2),
        })

        packet = json.dumps(self.data)
        showInfo(
            self.data["volante"],
            self.data["acceleratore"],
            self.data["freno"]
        )


