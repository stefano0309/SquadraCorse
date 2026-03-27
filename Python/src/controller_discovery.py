import pygame
import time

# ══════════════ DISCOVERY ══════════════
def scopri_assi(js) -> dict:
    print(f"\n  Controller : {js.get_name()}")
    print(f"  Assi       : {js.get_numaxes()}")
    print("\n  --- MAPPATURA ASSI (muovi l'asse, timeout 10 s) ---\n")
    nomi = ["STERZO", "ACCELERATORE", "FRENO"]
    assi: dict[str, dict] = {}
    used_indices: set[int] = set()
    t0 = time.time()
    while time.time() - t0 < 0.5:
        pygame.event.pump()
        time.sleep(0.02)
    for nome in nomi:
        print(f"  {nome}: ", end="", flush=True)
        pygame.event.pump()
        baseline = [js.get_axis(i) for i in range(js.get_numaxes())]
        trovato = False
        deadline = time.time() + 10
        while not trovato and time.time() < deadline:
            pygame.event.pump()
            for i in range(js.get_numaxes()):
                val = js.get_axis(i)
                if abs(val - baseline[i]) > 0.25 and i not in used_indices:
                    # Asse rilevato: registra riposo e continua a leggere per il picco
                    rest = baseline[i]
                    peak = val
                    t_peak = time.time()
                    while time.time() - t_peak < 0.6:
                        pygame.event.pump()
                        cur = js.get_axis(i)
                        if abs(cur - rest) > abs(peak - rest):
                            peak = cur
                        time.sleep(0.02)
                    assi[nome] = {"idx": i, "rest": round(rest, 3), "peak": round(peak, 3)}
                    used_indices.add(i)
                    print(f"asse {i}  (riposo: {rest:+.2f}, picco: {peak:+.2f})")
                    trovato = True
                    time.sleep(0.2)
                    break
            time.sleep(0.02)
        if not trovato:
            print("non rilevato")
    return assi

def scopri_pulsanti(js) -> dict:
    print("\n  --- MAPPATURA PULSANTI (premi il pulsante, timeout 10 s) ---\n")
    nomi = ["VEL_SU", "VEL_GIU", "RETRO", "MENU"]
    buttons: dict[str, int] = {}
    for nome in nomi:
        print(f"  {nome}: ", end="", flush=True)
        time.sleep(0.3)
        pygame.event.clear()
        pygame.event.pump()
        trovato = False
        deadline = time.time() + 10
        while not trovato and time.time() < deadline:
            for ev in pygame.event.get():
                if ev.type == pygame.JOYBUTTONDOWN:
                    btn = ev.button
                    if btn not in buttons.values():
                        buttons[nome] = btn
                        print(f"pulsante {btn}")
                        trovato = True
                        while any(e.type == pygame.JOYBUTTONUP and e.button == btn for e in pygame.event.get()):
                            pass
                        time.sleep(0.15)
                        break
            if not trovato:
                pygame.event.pump()
                for i in range(js.get_numbuttons()):
                    if js.get_button(i) and i not in buttons.values():
                        buttons[nome] = i
                        print(f"pulsante {i} (poll)")
                        trovato = True
                        while js.get_button(i):
                            pygame.event.pump()
                            time.sleep(0.02)
                        time.sleep(0.15)
                        break
            time.sleep(0.02)
        if not trovato:
            print("non rilevato")
    return buttons