import pygame

pygame.init()
pygame.joystick.init()

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
                    print("Menu principale richiamato.")
                    print("X - Seleziona exit")
                    print("PS button - Menu start")
                    print("Avvio del veicolo...")
                    start = True
                else:
                    start = False


            if event.button == 5:
                print("Exit selezionato. Uscita dal programma.")
                running = False
    
        if start:
            if event.type == pygame.JOYAXISMOTION:
                    print(f"Asse: {event.axis} Velocità attuale: {event.value:.2f}")
                

pygame.quit()
