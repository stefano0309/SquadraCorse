import pygame
import os
import json
import time
from colorama import Fore, Back, Style, init


init(autoreset=True)
"""
print(Fore.RED + 'Testo Rosso')
print(Back.GREEN + 'Testo con sfondo Verde')
print(Style.BRIGHT + Fore.CYAN + 'Testo Ciano brillante')
print('Testo normale (grazie ad autoreset=True)')
"""



pygame.init()
pygame.joystick.init()
data = {}

if pygame.joystick.get_count() == 0:
    print("Nessun controller trovato.")
    pygame.quit()
    quit()

js = pygame.joystick.Joystick(0)
js.init()

print(Fore.YELLOW + "Controller connesso correttamente:" + Style.RESET_ALL)
print(f"\t- Volante rilevato: {js.get_name()}")
print(f"\t- Numero di pulsanti: {js.get_numbuttons()}")
print(f"\t- Numero di assi: {js.get_numaxes()}")

print(Fore.YELLOW+ "\nCLICCARE PULSANTE PS PER INIZIARE" + Style.RESET_ALL)
fistStart = True

running = True
start = False
settings = False
selectItem = False

positionNow = 0
maxVelocity = 0
selected = 0

option_selected = ["Regolazione massima velocità", "Altre impostazioni future"]

while running:
    for event in pygame.event.get():

        #----- Uscita dal programma tastiera------

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.JOYBUTTONDOWN:
            print(f"Pulsante premuto: {event.button}")

            #------ Menu principale / Avvio e stop veicolo ------
            
            if event.button == 12:
                if fistStart:
                    fistStart = False
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.YELLOW +  "Menu principale:" + Style.RESET_ALL)
                    print("\tQUADRATO - Impostazioni veicolo")
                    print("\tPS button - Menu/start/stop veicolo")
                    print(Fore.RED + "\tX - Seleziona exit" + Style.RESET_ALL)
                    print("Avvio del veicolo...")
                    start = True
                elif start == False:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.YELLOW +  "Menu principale:" + Style.RESET_ALL)
                    print("\tQUADRATO - Impostazioni veicolo")
                    print("\tPS button - Menu/start/stop veicolo")
                    print(Fore.RED + "\tX - Seleziona exit" + Style.RESET_ALL)
                    print("Avvio del veicolo...")
                    start = True
                else:
                    start = False
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.YELLOW +  "Menu principale:" + Style.RESET_ALL)
                    print("\tQUADRATO - Impostazioni veicolo")
                    print("\tPS button - Menu/start/stop veicolo")
                    print(Fore.RED + "\tX - Seleziona exit" + Style.RESET_ALL)
                    print("Avvio del veicolo...")
                    
            #------ Uscita programma ------

            if event.button == 5 and start == False and settings == False:
                print("Exit selezionato. Uscita dal programma.")
                running = False
            

            #------ Impostazioni veicolo ------
            
            if not settings:
                if event.button == 3 and start == False:
                    settings = True
                    selected = 0
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("Impostazioni veicolo selezionate.")
                    
                    for idx, option in enumerate(option_selected, start=1):
                        if idx - 1 == selected:
                            print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
                        else: 
                            print(f"\t{idx}. {option}")
                    print("Premi CERCHIO per selezionare l'opzione.")     
                    print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)
            
            if settings:
                if event.button == 0:
                    selectItem = False
                    if selected == 0:
                        selected = 0
                    else:
                        selected -=1
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("Impostazioni veicolo selezionate.")
                    for idx, option in enumerate(option_selected, start=1):
                        if idx - 1 == selected:
                            print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
                        else: 
                            print(f"\t{idx}. {option}")
                    print("Premi CERCHIO per selezionare l'opzione.")
                    print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)

                if event.button == 1:
                    selectItem = False
                    if selected == len(option_selected) - 1:
                        selected = len(option_selected) - 1
                    else:
                        selected +=1
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("Impostazioni veicolo selezionate.")
                    for idx, option in enumerate(option_selected, start=1):
                        if idx - 1 == selected:
                            print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
                        else: 
                            print(f"\t{idx}. {option}")
                    print("Premi CERCHIO per selezionare l'opzione.")
                    print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)

                if event.button == 4 :
                    
                    if selectItem:
                        selectItem = False
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Impostazioni veicolo selezionate.")
                        for idx, option in enumerate(option_selected, start=1):
                            if idx - 1 == selected:
                                print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
                            else: 
                                print(f"\t{idx}. {option}")
                        print("Premi CERCHIO per selezionare l'opzione.")
                        print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)
                
                    else:
                        selectItem = True
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Impostazioni veicolo selezionate.")
                        for idx, option in enumerate(option_selected, start=1):
                            if idx - 1 == selected:
                                print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
                                if selected == 0:
                                    print(Fore.CYAN + "\t   0%" + Style.RESET_ALL, end=' ')
                                    [print(Fore.CYAN + "|"+ Style.RESET_ALL, end='') for x in range(int(maxVelocity / 5))]
                                    [print("|", end='') for x in range(20-int(maxVelocity/5))]
                                    print(Fore.CYAN+ f" 100% > {maxVelocity}" + Style.RESET_ALL) 
                            else: 
                                print(f"\t{idx}. {option}")
                        print("Premi CERCHIO per selezionare l'opzione.")
                        print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)
                
                if event.button == 5:
                    settings = False
                    selectItem = False
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.YELLOW +  "Menu principale:" + Style.RESET_ALL)
                    print("\tQUADRATO - Impostazioni veicolo")
                    print("\tPS button - Menu/start/stop veicolo")
                    print(Fore.RED + "\tX - Seleziona exit" + Style.RESET_ALL)
                    print("Avvio del veicolo...")

        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0 and selected == 0 and selectItem :
                
                if event.value > 0 and event.value > positionNow:
                    if maxVelocity >= 100:
                        maxVelocity = 100
                    else:
                        maxVelocity += 1
                else:
                    if maxVelocity <= 0:
                        maxVelocity = 0
                    else:
                        maxVelocity -= 1
                positionNow = event.value
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Impostazioni veicolo selezionate.")
                for idx, option in enumerate(option_selected, start=1):
                    if idx - 1 == selected:
                        print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
                        if selected == 0:
                            print(Fore.CYAN + "\t   0%" + Style.RESET_ALL, end=' ')
                            [print(Fore.CYAN + "|"+ Style.RESET_ALL, end='') for x in range(int(maxVelocity / 5))]
                            [print("|", end='') for x in range(20-int(maxVelocity/5))]
                            print(Fore.CYAN+ f" 100% > {maxVelocity}" + Style.RESET_ALL) 
                    else: 
                        print(f"\t{idx}. {option}")
                print("Premi CERCHIO per selezionare l'opzione.")
                print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)


        #------ Invio dati assi ------
    
        if start:
            if event.type == pygame.JOYAXISMOTION:
                data.update({
                    "volante": round(js.get_axis(0),2),
                    "acceleratore": round(js.get_axis(5),2),
                    "freno": round(js.get_axis(1),2),
                })
                packet = json.dumps(data)
                print("Inviato:", packet)
            else:
                data.update({
                    "volante": round(js.get_axis(0),2),
                    "acceleratore": round(js.get_axis(5),2),
                    "freno": round(js.get_axis(1),2),
                })
                
           
pygame.quit()