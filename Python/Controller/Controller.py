import pygame
import json
import os

class PS4Controller:
    def __init__(self, map_file="button_map.json"):
        self.map_file = map_file
        self.axis_value = {}  
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise Exception("Nessun controller trovato.")
        self.js = pygame.joystick.Joystick(0)
        self.js.init()
        print(f"Controller rilevato: {self.js.get_name()}")

        # Lista dei tasti da mappare
        self.ordered_buttons = [
            "X","Cerchio","Quadrato","Triangolo",
            "L1","R1","L2","R2",
            "Share","Options",
            "L3","R3","PS Button"
        ]
        self.button_mapping = {}  # Nome tasto -> ID
        self.button_state = {}    # ID -> True/False

        # Se esiste file di mappatura, caricalo
        if os.path.exists(self.map_file):
            self.load_mapping()
        else:
            self.map_controller()   # altrimenti esegui la fase di mappatura
            self.save_mapping()

    def map_controller(self):
        print("FASE DI MAPPATURA: premi i tasti nell'ordine indicato...")
        for tasto in self.ordered_buttons:
            mapped = False
            while not mapped:
                for event in pygame.event.get():
                    if event.type == pygame.JOYBUTTONDOWN:
                        btn = event.button
                        if btn not in self.button_mapping.values():
                            self.button_mapping[tasto] = btn
                            self.button_state[btn] = False
                            print(f"{tasto} mappato con ID {btn}")
                            mapped = True
                    if event.type == pygame.JOYHATMOTION:
                        hat_x, hat_y = event.value
                        if tasto == "D-PAD SU" and hat_y == 1:
                            self.button_mapping[tasto] = "HAT_UP"; mapped=True; print(f"{tasto} mappato")
                        if tasto == "D-PAD GIÙ" and hat_y == -1:
                            self.button_mapping[tasto] = "HAT_DOWN"; mapped=True; print(f"{tasto} mappato")
                        if tasto == "D-PAD SINISTRA" and hat_x == -1:
                            self.button_mapping[tasto] = "HAT_LEFT"; mapped=True; print(f"{tasto} mappato")
                        if tasto == "D-PAD DESTRA" and hat_x == 1:
                            self.button_mapping[tasto] = "HAT_RIGHT"; mapped=True; print(f"{tasto} mappato")
                    if event.type == pygame.JOYAXISMOTION:
                        if tasto == "L2" and event.axis == 4 and event.value > 0.5:
                            self.button_mapping[tasto] = "AXIS4"; mapped=True; print(f"{tasto} mappato")
                        if tasto == "R2" and event.axis == 5 and event.value > 0.5:
                            self.button_mapping[tasto] = "AXIS5"; mapped=True; print(f"{tasto} mappato")
                        

    def get_R2(self):
        self.update()  # aggiorna eventi
        return self.axis_value.get("R2", 0.0)
    
    def get_L2(self):
        self.update()  # aggiorna eventi
        return self.axis_value.get("L2", 0.0)
    
    def get_RX(self):
        self.update()  # aggiorna eventi
        return self.axis_value.get("RX", 0.0)


    def save_mapping(self):
        with open(self.map_file, "w") as f:
            json.dump(self.button_mapping, f, indent=4)
        print(f"Mappatura salvata su {self.map_file}")

    def load_mapping(self):
        with open(self.map_file, "r") as f:
            self.button_mapping = json.load(f)
        # Inizializza lo stato dei tasti
        for val in self.button_mapping.values():
            if isinstance(val, int):
                self.button_state[val] = False
        print(f"Mappatura caricata da {self.map_file}")

    def update(self):
        # Aggiorna lo stato dei pulsanti
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in self.button_state:
                    self.button_state[event.button] = True
            if event.type == pygame.JOYBUTTONUP:
                if event.button in self.button_state:
                    self.button_state[event.button] = False
            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 3:  # L2
                    self.axis_value["L2"] = (event.value + 1) / 2  # scala 0-1
                if event.axis == 2:  # R2
                    self.axis_value["R2"] = (event.value + 1) / 2  # scala 0-1
                if event.axis == 0:  
                    self.axis_value["RX"] = event.value  # valore da -1.0 a 1.0
 