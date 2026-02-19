import os
from colorama import * 
from datetime import *
import json
from art import *
import struct
      
BINARY_MARKER = 170


#---- Funzioni setUp ----

def setUpWorkSpace():
    path = os.getcwd()+"\\src"
    if not os.path.exists(path+"\\data"):
        print(Fore.YELLOW + "Setting up workspace" + Style.RESET_ALL)
        os.makedirs(path+"\\data")
        os.makedirs(path+"\\data\\preset")
        with open(path+"\\data\\preset\\preset0.json", "w") as f:
            data = {
                "maxVel": 50,
                "maxAngle": 45
            }
            json.dump(data, f, indent=4)

        with open(path+"\\data\\preset\\indexPreset.json", "w") as f:
            data = {
                "presetNames": ["start"],
                "preset": "start"
            }
            json.dump(data, f, indent=4)

        with open(path+"\\data\\setting.json", "w") as f:
            data = {
                "dateTime": str(datetime.now()),
                "paths": {
                    "homePath": path,
                    "dataPath": path+"\\data",
                    "settingPath": path+"\\data\\setting.json",
                    "presetPath": path+"\\data\\preset",
                    "presetIndex": path+"\\data\\preset\\indexPreset.json",
                    "configPath": path+"\\data\\config.json"
                },
                "presetButton": ["12","5","3","0","1","4","9","8"],
                "presetAxis": ["0","5","1"]
            }
            json.dump(data, f, indent=4)

#--- Funzioni di preset ---

def readfile(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def writefile(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def loadWorkSpace():
    setUpWorkSpace()
    data = readfile(os.getcwd()+"\\src\\data\\setting.json")
    PATHS = data["paths"]
    BUTTON = data["presetButton"]
    AXIS = data["presetAxis"]
    return PATHS, BUTTON, AXIS


# Funzione helper per validare gli input numerici
def get_int_input(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
        except ValueError:
            pass
        print(f"Errore: inserire un numero tra {min_val} e {max_val}")

def presetMenu(presetIndex, presetPath, vel=50, angle=45):
    CLEAR()
    print(Fore.YELLOW + "Gestione PRESET" + Style.RESET_ALL)
    print("\t1. Salva attuale\n\t2. Crea nuovo\n\t3. Carica esistente")
    
    scelta = get_int_input("Opzione -> ", 1, 3)
    
    if scelta == 1:
        savePreset(presetIndex, presetPath, vel, angle)
    elif scelta == 2:
        createPreset(presetIndex, presetPath, vel, angle)
    else:
        return loadPreset(presetIndex, presetPath)

def savePreset(presetIndex, presetPath, vel, angle):
    data = readfile(presetIndex)
    index = data["presetNames"].index(data["preset"])
    
    payload = {"maxVel": vel, "maxAngle": angle}
    writefile(f"{presetPath}\\preset{index}.json", payload)
    print(Fore.GREEN + "Preset salvato correttamente!" + Style.RESET_ALL)

def createPreset(presetIndex, presetPath, vel, angle):
    CLEAR()
    data = readfile(presetIndex)
    names = data["presetNames"]

    # Validazione nome unico
    name = ""
    while not name or name in names:
        name = input("Inserisci un nome univoco per il preset: ").lower().strip()
    
    names.append(name)
    
    if input("Vuoi inserire i valori manualmente? (y/n): ").lower() == "y":
        vel = get_int_input("Velocità (1-100): ", 1, 100)
        angle = get_int_input("Angolo (1-180): ", 1, 180)

    # Aggiorna indice nomi
    use_now = input("Usare subito questo preset? (y/n): ").lower() == "y"
    data["preset"] = name if use_now else data["preset"]
    writefile(presetIndex, data)

    # Salva file fisico del preset
    save_data = {"maxVel": vel, "maxAngle": angle}
    writefile(f"{presetPath}\\preset{len(names)-1}.json", save_data)

def loadPreset(presetIndex, presetPath):
    data = readfile(presetIndex)
    names = data["presetNames"]

    print(Fore.YELLOW + "Preset disponibili:")
    for i, name in enumerate(names):
        print(f"\t{i}. {name.capitalize()}")

    idx = get_int_input("\tScegli il numero del preset: ", 0, len(names) - 1)
    
    # Aggiorna il preset attivo nel file indice
    data["preset"] = names[idx]
    writefile(presetIndex, data)

    # Carica i valori reali
    vel, angle = reloadPreset(presetIndex, presetPath)
    print(f"Caricato: {names[idx].upper()} (Vel: {vel}, Angolo: {angle})")
    return vel, angle

def reloadPreset(presetIndex, presetPath):
    data_idx = readfile(presetIndex)
    idx = data_idx["presetNames"].index(data_idx["preset"])
    
    preset_data = readfile(f"{presetPath}\\preset{idx}.json")
    return preset_data["maxVel"], preset_data["maxAngle"]


def configMenu(path):
    print(Fore.YELLOW + "Menu di configurazione:" + Style.RESET_ALL)
    if os.path.exists(path):
        print(Fore.GREEN + "\nFile di configurazione trovato \n" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "\nFile di configurazione non trovato" + Style.RESET_ALL)
        print(Fore.YELLOW + "\nCreazione di una configurazione:")
        print("Configurazione:\n\t- Se il campo e vuoto viene caricato un preset\n\t- Se inserisci un valore verra creata una configurazione personalizata")
        
def buttonMap(presetButton, presetAxis, button, axis, path):
    dataButton = {}
    dataAxis = {}
    data = {}
    configMenu(path)
    if not os.path.exists(path):
        print(Fore.GREEN + "Configurazione buttoni:" + Style.RESET_ALL)
        for idx, btn in enumerate(button):
            btnValue = input(f"{btn}: ")
            if btnValue == "":
                btnValue = presetButton[idx]
                print("Caricato preset con id", presetButton[idx])
            dataButton.update({
                btn: btnValue
            })
        print(Fore.GREEN + "Configurazione assi:" + Style.RESET_ALL)
        for idx, x in enumerate(axis):
            axisValue = input(f"{x}: ")
            if axisValue == "":
                axisValue = presetAxis[idx]
                print("Caricato preset con id", presetAxis[idx])
            dataAxis.update({
                x: axisValue
            })
        data.update({
            "button": dataButton,
            "axis": dataAxis
        })
        with open(path, mode="w") as f:
            json.dump(data, f, indent=4)

def loadMap(path):
    with open(path, mode="r") as f:
        dati = json.load(f)
        buttons = {k: int(v) for k, v in dati["button"].items()}
        axis = {k: int(v) for k, v in dati["axis"].items()}
    return buttons, axis

#---- Funzioni generali ----

def CLEAR():
    os.system('cls' if os.name == 'nt' else 'clear')

def INIZIALISE(js):
    print(text2art("Squadra Corse", font="small"))
    print(Fore.YELLOW + "Controller connesso correttamente:" + Style.RESET_ALL)
    print(f"\t- Volante rilevato: {js.get_name()}")
    print(f"\t- Numero di pulsanti: {js.get_numbuttons()}")
    print(f"\t- Numero di assi: {js.get_numaxes()}")
    print(Fore.YELLOW+ "\nCLICCARE PULSANTE PS PER ANDARE AVANTI" + Style.RESET_ALL)

#---- Funzioni programma -----

def drawMenu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.YELLOW +  "Menu principale:" + Style.RESET_ALL)
    print("\tQUADRATO - Impostazioni veicolo")
    print("\tPS button - Menu/start/stop veicolo")
    print(Fore.RED + "\tX - Seleziona exit" + Style.RESET_ALL)
    print("Avvio del veicolo...")


def drawSettings(slx, opt):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Impostazioni veicolo selezionate.")
    for idx, option in enumerate(opt, start=1):
        if idx - 1 == slx:
            print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
        else: 
            print(f"\t{idx}. {option}")
    print("Premi CERCHIO per selezionare l'opzione.")     
    print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)

def settingOption(value, position, max, min, var, id, idValue, subdivision, opt):
    if value > 0 and value > position:
        if var >= max:
            var = max
        else:
            var += 1
    else:
        if var <= min:
            var = min
        else:
            var -= 1
    position= value
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Impostazioni veicolo selezionate.")
    for idx, option in enumerate(opt, start=1):
        if idx - 1 == id:
            print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
            if id == idValue:
                drawSettingOption(min, max, var, subdivision)
        else: 
            print(f"\t{idx}. {option}")
    print("Premi CERCHIO per selezionare l'opzione.")
    print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)
    return position, var

def drawSettingOption(min, max, var, subdivision):
    print(Fore.CYAN + f"\t   {min}" + Style.RESET_ALL, end=' ')
    [print(Fore.CYAN + "|"+ Style.RESET_ALL, end='') for x in range(int(var / subdivision))]
    [print("|", end='') for x in range(20-int(var/subdivision))]
    print(Fore.CYAN+ f" {max} > {var}" + Style.RESET_ALL) 

def showInfo(volante, acceleratore, freno):
    print("VOLANTE: "+str(volante), "ACCELERATORE: "+str(acceleratore), "FRENO: "+ str(freno))
            
def crc16_ccitt(data: bytes) -> int:
    """Calcola il checksum CRC-16 CCITT necessario per l'integrità del pacchetto."""
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if (crc & 0x8000) else (crc << 1)
            crc &= 0xFFFF
    return crc #

def genera_pacchetto(steer, accel, brake, speed_sel, reverse, commands=0):
    """
    Comprime i dati nel formato binario richiesto dal protocollo.
    """
    # Clipping dei valori (0-255 per gli assi, 0-15 per le marce)
    steer = max(0, min(255, int(steer)))
    accel = max(0, min(255, int(accel)))
    brake = max(0, min(255, int(brake)))
    speed_sel = max(0, min(15, int(speed_sel)))
    
    # Costruzione del byte 'misc': [Marcia(4bit) | Retro(1bit) | Comandi(3bit)]
    misc = ((speed_sel & 0x0F) << 4) | ((1 if reverse else 0) << 3) | (commands & 0x07)
    
    # Composizione del payload e calcolo checksum
    payload = bytes([steer, accel, brake, misc]) 
    crc = crc16_ccitt(payload)
    
    # Frame finale: Marker + Payload + CRC (2 byte Big Endian)
    return bytes([BINARY_MARKER]) + payload + struct.pack(">H", crc)