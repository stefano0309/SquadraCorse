import os
from colorama import * 

#---- Funzioni generali ----

def CLEAR():
    os.system('cls' if os.name == 'nt' else 'clear')

def INIZIALISE(js):
    print(Fore.YELLOW + "Controller connesso correttamente:" + Style.RESET_ALL)
    print(f"\t- Volante rilevato: {js.get_name()}")
    print(f"\t- Numero di pulsanti: {js.get_numbuttons()}")
    print(f"\t- Numero di assi: {js.get_numaxes()}")
    print(Fore.YELLOW+ "\nCLICCARE PULSANTE PS PER INIZIARE" + Style.RESET_ALL)

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
        
