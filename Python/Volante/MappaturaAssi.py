import pygame

pygame.init()

pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("Nessun controller trovato.")
    quit()

js = pygame.joystick.Joystick(0)
js.init()
print(f"Volante rilevato: {js.get_name()}")
print(f"Numero di pulsanti: {js.get_numbuttons()}")
print(f"Numero di assi: {js.get_numaxes()}")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    for axe in range(js.get_numaxes()):
        print(f"asse{axe}: {js.get_axis(axe)}")
    pygame.display.flip()

pygame.quit()