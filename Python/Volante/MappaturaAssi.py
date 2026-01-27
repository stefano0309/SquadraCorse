import pygame
import os
import json
import time



pygame.init()
pygame.joystick.init()
data = {}

if pygame.joystick.get_count() == 0:
    print("Nessun controller trovato.")
    pygame.quit()
    quit()

js = pygame.joystick.Joystick(0)
js.init()

print(f"Volante rilevato: {js.get_name()}")
print(f"Numero di pulsanti: {js.get_numbuttons()}")
print(f"Numero di assi: {js.get_numaxes()}")

print("PS button menu principale richiamato")
running = True
start = False
settings = False
maxVelocity = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.JOYBUTTONDOWN:
            print(f"Pulsante premuto: {event.button}")
            
            if event.button == 12:
                if start == False:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("Menu principale richiamato.")
                    print("❌ - Seleziona exit")
                    print("⬜ - Impostazioni veicolo")
                    print("PS button - Menu start")
                    print("Avvio del veicolo...")
                    start = True
                else:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("Stop veicolo...")
                    print("Menu principale richiamato.")
                    print("❌ - Seleziona exit")
                    print("⬜ - Impostazioni veicolo")
                    print("PS button - Menu/start/stop veicolo")
                    print("Avvio del veicolo...")
                    start = False


            if event.button == 5 and start == False and settings == False:
                print("Exit selezionato. Uscita dal programma.")
                running = False
            if event.button == 5 and settings:
                settings = False
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Tornato al menu principale.")
                print("❌ - Seleziona exit")
                print("⬜ - Impostazioni veicolo")
                print("PS button - Menu/start/stop veicolo")
                print("Avvio del veicolo...")
            if event.button == 3 and start == False:
                settings = True
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Impostazioni veicolo selezionate.")
                print("\t- Regolazione massima velocità")
                print("Premi ❌ per tornare al menu principale.")

    
        if start:
            
            if event.type == pygame.JOYAXISMOTION:
                    data.update({
                        "volante" if event.axis == 0 else "acceleratore" if event.axis==5 else "freno" if event.axis==1 else "altro": round(event.value, 2),
                    })
                
            packet = json.dumps(data)      
            print("Inviato:", packet)
pygame.quit()