import pygame
import math

pygame.init()
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PS4 Controller Dashboard")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (50, 200, 50)
RED   = (255, 80, 80)
BLUE  = (50, 120, 255)
YELLOW = (255, 200, 50)

FONT = pygame.font.SysFont("Arial", 18)
clock = pygame.time.Clock()

pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("Nessun controller trovato.")
    quit()

js = pygame.joystick.Joystick(0)
js.init()
print(f"Controller rilevato: {js.get_name()}")

# -------------------------
# Definizione tasti nell'ordine di mappatura
# -------------------------
ordered_buttons = [
    "X", "Cerchio", "Quadrato", "Triangolo",
    "L1", "R1", "L2", "R2",
    "Share", "Options",
    "L3", "R3", "PS Button"
]

button_mapping = {}   # Nome del tasto -> ID rilevato
button_state = {}     # ID -> stato True/False

# -------------------------
# Fase di mappatura
# -------------------------
print("FASE DI MAPPATURA: premi i tasti nell'ordine indicato...")
for tasto in ordered_buttons:
    mapped = False
    while not mapped:
        for event in pygame.event.get():
            # Pulsanti fisici
            if event.type == pygame.JOYBUTTONDOWN:
                btn = event.button
                if btn not in button_mapping.values():
                    button_mapping[tasto] = btn
                    button_state[btn] = False
                    print(f"{tasto} mappato con ID {btn}")
                    mapped = True
            # D-PAD
            if event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if tasto == "D-PAD SU" and hat_y == 1:
                    button_mapping[tasto] = "HAT_UP"
                    mapped = True
                elif tasto == "D-PAD GIÙ" and hat_y == -1:
                    button_mapping[tasto] = "HAT_DOWN"
                    mapped = True
                elif tasto == "D-PAD SINISTRA" and hat_x == -1:
                    button_mapping[tasto] = "HAT_LEFT"
                    mapped = True
                elif tasto == "D-PAD DESTRA" and hat_x == 1:
                    button_mapping[tasto] = "HAT_RIGHT"
                    mapped = True
                if mapped:
                    print(f"{tasto} mappato")
            # Trigger L2/R2
            if event.type == pygame.JOYAXISMOTION:
                if tasto == "L2" and event.axis == 4 and event.value > 0.5:
                    button_mapping[tasto] = "AXIS4"
                    mapped = True
                    print(f"{tasto} mappato (asse 4)")
                if tasto == "R2" and event.axis == 5 and event.value > 0.5:
                    button_mapping[tasto] = "AXIS5"
                    mapped = True
                    print(f"{tasto} mappato (asse 5)")

print("\nMappatura completata! ID tasti:")
for tasto, id_value in button_mapping.items():
    print(f"{tasto}: {id_value}")

# -------------------------
# Dashboard
# -------------------------
AREA_RADIUS = 70
DOT_RADIUS = 12
left_center  = (200, HEIGHT // 2)
right_center = (700, HEIGHT // 2)
left_x, left_y   = left_center
right_x, right_y = right_center

trigger_L2 = 0
trigger_R2 = 0
dpad_x = 0
dpad_y = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Pulsanti fisici
        if event.type == pygame.JOYBUTTONDOWN:
            btn = event.but ton
            if btn in button_state:
                button_state[btn] = True
        if event.type == pygame.JOYBUTTONUP:
            btn = event.button
            if btn in button_state:
                button_state[btn] = False

        # Stick e trigger
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0: left_x = left_center[0] + event.value * AREA_RADIUS
            if event.axis == 1: left_y = left_center[1] + event.value * AREA_RADIUS
            if event.axis == 2: right_x = right_center[0] + event.value * AREA_RADIUS
            if event.axis == 3: right_y = right_center[1] + event.value * AREA_RADIUS
            if event.axis == 4: trigger_L2 = (event.value + 1) / 2
            if event.axis == 5: trigger_R2 = (event.value + 1) / 2

        # D-PAD
        if event.type == pygame.JOYHATMOTION:
            dpad_x, dpad_y = event.value

    # Limite circolare stick
    for cx, cy, x, y in [(left_center[0], left_center[1], left_x, left_y),
                         (right_center[0], right_center[1], right_x, right_y)]:
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > AREA_RADIUS:
            scale = AREA_RADIUS / dist
            if (cx, cy) == left_center:
                left_x = cx + dx * scale
                left_y = cy + dy * scale
            else:
                right_x = cx + dx * scale
                right_y = cy + dy * scale

    # ---------------------------
    # Disegno grafica
    # ---------------------------
    screen.fill(WHITE)

    # Stick sinistro
    pygame.draw.circle(screen, BLACK, left_center, AREA_RADIUS, 2)
    pygame.draw.circle(screen, RED, (int(left_x), int(left_y)), DOT_RADIUS)
    screen.blit(FONT.render("Stick Sinistro", True, BLACK),
                (left_center[0] - 50, left_center[1] + AREA_RADIUS + 10))

    # Stick destro
    pygame.draw.circle(screen, BLACK, right_center, AREA_RADIUS, 2)
    pygame.draw.circle(screen, RED, (int(right_x), int(right_y)), DOT_RADIUS)
    screen.blit(FONT.render("Stick Destro", True, BLACK),
                (right_center[0] - 50, right_center[1] + AREA_RADIUS + 10))

    # Trigger
    pygame.draw.rect(screen, GRAY, (150, 50, 200, 20))
    pygame.draw.rect(screen, BLUE, (150, 50, int(200 * trigger_L2), 20))
    screen.blit(FONT.render("L2", True, BLACK), (100, 50))

    pygame.draw.rect(screen, GRAY, (550, 50, 200, 20))
    pygame.draw.rect(screen, BLUE, (550, 50, int(200 * trigger_R2), 20))
    screen.blit(FONT.render("R2", True, BLACK), (510, 50))

    # D-PAD
    dpad_center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, GREEN if dpad_y==1 else GRAY,    (dpad_center[0]-20, dpad_center[1]-60,40,40))
    pygame.draw.rect(screen, GREEN if dpad_y==-1 else GRAY,   (dpad_center[0]-20, dpad_center[1]+20,40,40))
    pygame.draw.rect(screen, GREEN if dpad_x==-1 else GRAY,   (dpad_center[0]-60, dpad_center[1]-20,40,40))
    pygame.draw.rect(screen, GREEN if dpad_x==1 else GRAY,    (dpad_center[0]+20, dpad_center[1]-20,40,40))
    screen.blit(FONT.render("D-Pad", True, BLACK), (dpad_center[0]-25, dpad_center[1]+70))

    # Pulsanti
    y_offset = 350
    x_offset = 40
    step = 130
    row = col = 0
    for tasto in ordered_buttons:
        id_val = button_mapping[tasto]
        state = False
        if isinstance(id_val, int):
            state = button_state.get(id_val, False)
        elif id_val == "HAT_UP": state = (dpad_y == 1)
        elif id_val == "HAT_DOWN": state = (dpad_y == -1)
        elif id_val == "HAT_LEFT": state = (dpad_x == -1)
        elif id_val == "HAT_RIGHT": state = (dpad_x == 1)
        elif id_val == "AXIS4": state = (trigger_L2 > 0.5)
        elif id_val == "AXIS5": state = (trigger_R2 > 0.5)

        bx = x_offset + col*step
        by = y_offset + row*35
        color = YELLOW if state else GRAY
        pygame.draw.rect(screen, color, (bx, by, 120, 30))
        screen.blit(FONT.render(tasto, True, BLACK), (bx+5, by+5))

        col += 1
        if col == 6:
            col = 0
            row += 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
