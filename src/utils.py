import os
from colorama import * 
import json

#---- Funzioni setUp ----

presetButton = ["12","5","3","0","1","4","9","8"]
presetAxis = ["0","5","1"]

def configMenu(path):
    print(Fore.YELLOW + "Menu di configurazione:" + Style.RESET_ALL)
    if os.path.exists(path):
        print(Fore.GREEN + "\nFile di configurazione trovato \n" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "\nFile di configurazione non trovato" + Style.RESET_ALL)
        print(Fore.YELLOW + "\nCreazione di una configurazione:")
        print("Configurazione:\n\t- Se il campo e vuoto viene caricato un preset\n\t- Se inserisci un valore verra creata una configurazione personalizata")
        
def buttonMap(button, axis, path):
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
        with open("config.json", mode="w") as f:
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
        
def loadPreset(path):
    files = os.listdir(path)
    for file in files:
        print(os.path.join(path,file))
