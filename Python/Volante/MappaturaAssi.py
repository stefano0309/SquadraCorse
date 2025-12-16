import pygame

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise Exception("Nessun volante collegato!")

wheel = pygame.joystick.Joystick(0)
wheel.init()

print("Volante rilevato:", wheel.get_name())
print("Assi disponibili:", wheel.get_numaxes())
print("Pulsanti disponibili:", wheel.get_numbuttons())
print("HAT disponibili:", wheel.get_numhats())

while True:
    pygame.event.pump()

    print("\n----- ASSI -----")
    for i in range(wheel.get_numaxes()):
        print(f"Asse {i}: {wheel.get_axis(i):.3f}")

    print("----- PULSANTI -----")
    for i in range(wheel.get_numbuttons()):
        print(f"Bottone {i}: {wheel.get_button(i)}")

    print("----- HAT -----")
    for i in range(wheel.get_numhats()):
        print(f"Hat {i}: {wheel.get_hat(i)}")

    pygame.time.wait(200)
