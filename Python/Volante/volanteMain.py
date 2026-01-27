import pygame
import json
from volanteFunzioni import *
from colorama import Fore, Back, Style, init


init(autoreset=True)
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
retromarcia = False

positionNow = 0
maxVelocity = 50
maxAngle = 45
selected = 0

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

            #----- Retromarcia / Inserita - Disinserita -----
            if event.button == 9:
                retromarcia = True
                print(Fore.GREEN + "Retromarcia inserita." + Style.RESET_ALL)
            
            if event.button == 8:
                retromarcia = False
                print(Fore.GREEN + "Retromarcia disinserita." + Style.RESET_ALL)
            #------ Menu principale / Avvio e stop veicolo ------
            if event.button == 12:
                if fistStart:
                    CLEAR()
                    fistStart = False
                    print("Avvio del veicolo...")
                    start = True
                elif start == False:
                    drawMenu()
                    start = True
                else:
                    start = False
                    drawMenu()
                    
            #------ Uscita programma ------
            if event.button == 5 and start == False and settings == False:
                print(Fore.GREEN + "Exit selezionato. Uscita dal programma." + Style.RESET_ALL)
                running = False

            #------ Impostazioni veicolo ------
            if not settings:
                if event.button == 3 and start == False:
                    settings = True
                    selected = 0
                    drawSettings(selected)
            
            if settings:
                if event.button == 0:
                    selectItem = False
                    if selected == 0:
                        selected = 0
                    else:
                        selected -=1
                    drawSettings(selected)

                if event.button == 1:
                    selectItem = False
                    if selected == len(option_selected) - 1:
                        selected = len(option_selected) - 1
                    else:
                        selected +=1
                    drawSettings(selected)

                if event.button == 4 :
                    positionNow = 0
                    if selectItem:
                        selectItem = False
                        drawSettings(selected)
                
                    else:
                        selectItem = True
                        CLEAR()
                        print("Impostazioni veicolo selezionate.")
                        for idx, option in enumerate(option_selected, start=1):
                            if idx - 1 == selected:
                                print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
                                if selected == 0:
                                    drawSettingOption(0,100,maxVelocity,5)
                                if selected == 1:
                                    drawSettingOption(0,180,maxAngle,9)
                            else: 
                                print(f"\t{idx}. {option}")
                        print("Premi CERCHIO per selezionare l'opzione.")
                        print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)
                
                if event.button == 5:
                    settings = False
                    selectItem = False
                    drawMenu()

        #------ Regolazione impostazioni ------

        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0  and selectItem :
                #----- Regolazione massima velocità ------
                if selected == 0:
                    positionNow, maxVelocity = settingOption(event.value, positionNow, 100, 0, maxVelocity, selected, 0, 5)
                    
                #----- Regolazione angolo massimo sterzo ------
                if selected == 1:
                    positionNow, maxAngle = settingOption(event.value, positionNow, 180, 0, maxAngle, selected, 1, 9)

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