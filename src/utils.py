import os
from colorama import * 
from datetime import *
import json

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



def loadWorkSpace():
    setUpWorkSpace()
    with open(os.getcwd()+"\\src\\data\\setting.json") as f:
        data = json.load(f)
        PATHS = data["paths"]
        BUTTON = data["presetButton"]
        AXIS = data["presetAxis"]
    return PATHS, BUTTON, AXIS


def presetMenu(presetIndex, presetPath, vel=50, angle=45):
    CLEAR()
    print(Fore.YELLOW + "Caricamento opzioni per il PRESET" + Style.RESET_ALL)
    print("\t1. Salvataggio preset\n\t2. Crea un preset\n\t3. Carica un preset")
    x = int(input("Opzione -> "))
    if x==1:
        savePreset(presetIndex, presetPath, vel, angle)
    elif x ==2:
        createPreset(presetIndex, presetPath, vel, angle)
    else:
        loadPreset(presetIndex, presetPath)

def savePreset(presetIndex, presetPath, vel , angle):
    CLEAR()
    print(Fore.YELLOW + "Salvataggio del preset con le impostazioni attuali" + Style.RESET_ALL)
    with open(presetIndex, "r") as f:
        data = json.load(f)
        index = data["presetNames"].index(data["preset"])
    with open(presetPath+f"\\preset{index}.json", "w") as f:
        data = {
            "maxVel": vel,
            "maxAngle": angle
        }
        json.dump(data, f)

def createPreset(presetIndex, presetPath, vel, angle):
    CLEAR()
    print(Fore.YELLOW + "Creazione di un preset in input/per impostazioni" + Style.RESET_ALL)
    with open(presetIndex, "r") as f:
        data = json.load(f)
        names = data["presetNames"]
        nameNow = data["preset"]
    
    name = input("Inserisci il nome del preset: ").lower()
    useName = True if name in names else False
    while useName:
        name = input("Inserisci il nome del preset: ").lower()
        useName = True if name in names else False
    names.append(name)

    index=len(names)-1

    usePreset = True if input("Vuoi usare questo preset da subito (y/n): ").lower() == "y" else False
    useInputs = True if input("Vuoi inserire i valori manualmente (y/n): ").lower() == "y" else False

    if useInputs:
        vel = int(input("Inserisci la velocità (1-100): "))
        while(vel<1 or vel>100):
            vel = int(input("Inserisci la velocità (1-100): "))
        angle = int(input("Inserisci angolo: "))
        while(angle<1 or angle>180):
             angle = int(input("Inserisci angolo: "))

    if usePreset:
        with open(presetIndex, "w") as f:
            data = {
                "presetNames": names,
                "preset": name
            }

            json.dump(data, f, indent=4)
    else:
        with open(presetIndex, "w") as f:
            data = {
                "presetNames": names,
                "preset": nameNow
            }

            json.dump(data, f, indent=4)
    
    with open(presetPath+f"\\preset{index}.json", "w") as f:
        data = {
            "maxVel": vel,
            "maxAngle": angle
        }
        json.dump(data, f, indent=4)

def loadPreset(presetIndex, presetPath):
    CLEAR()
    with open(presetIndex, "r") as f:
        data = json.load(f)
        names = data["presetNames"]
    print(Fore.YELLOW + "Preset possibili:")
    for x, name in enumerate(names):
        print(f"\t{x}. {name.capitalize()}")
    x = int(input(Fore.CYAN + "\tInserisci il numero del preset che vuoi caricare: " + Style.RESET_ALL))
    while(x<0 or x>len(name)-1):
        x = int(input(Fore.CYAN + "\tInserisci il numero del preset che vuoi caricare: " + Style.RESET_ALL))

    with open(presetIndex, "w") as f:
        data = {
            "presetNames":names,
            "preset": names[x]
        }
        json.dump(data, f, indent=4)
    print(Fore.YELLOW + "Caricamento del preset selezionato" + Style.RESET_ALL)
    vel, angle = reloadPreset(presetIndex, presetPath, names[x])
    print("Nome: " + Fore.CYAN + names[x].capitalize()+":" + Style.RESET_ALL +f"\n\t-Velocità: {vel}\n\t-Angolo: {angle}")
    return vel, angle

def reloadPreset(presetIndex, presetPath, name):
    with open(presetIndex, "r") as f:
        data = json.load(f)
        index = data["presetNames"].index(data["preset"])
    with open(presetPath+f"\\preset{index}.json", "r") as f:
        data = json.load(f)
        vel = data["maxVel"]
        angle = data["maxAngle"]
    return vel, angle    


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
        



def INIZIALISE_DEBUG():
    print(Fore.CYAN + "MODALITÀ DEBUG TASTIERA" + Style.RESET_ALL)
    print("\t- Volante: SIMULATO (WASD)")
    print("\t- Pulsanti: SIMULATI (S, P, Invio, Backspace, R, F)")
    print(Fore.YELLOW + "\nPREMI 'S' PER INIZIARE" + Style.RESET_ALL)
    