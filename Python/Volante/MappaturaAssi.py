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

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.JOYBUTTONDOWN:
            print(f"Pulsante premuto: {event.button}")

    for axe in range(js.get_numaxes()):
        value = js.get_axis(axe)
        print(f"Asse {axe}: {value:.3f}")

    print("-" * 30)
    clock.tick(10)  # 10 aggiornamenti al secondo

pygame.quit()
