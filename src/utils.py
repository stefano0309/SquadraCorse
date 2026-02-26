import json
import os
import time
from datetime import datetime
from pathlib import Path

import pygame
from art import text2art
from colorama import Fore, Style

BINARY_MARKER = 0xAA


def _repo_src_path() -> Path:
    return Path(__file__).resolve().parent


def setUpWorkSpace():
    src_path = _repo_src_path()
    data_path = src_path / "data"
    preset_path = data_path / "preset"

    data_path.mkdir(parents=True, exist_ok=True)
    preset_path.mkdir(parents=True, exist_ok=True)

    preset0 = preset_path / "preset0.json"
    if not preset0.exists():
        writefile(preset0, {"maxVel": 50, "maxAngle": 45})

    index_preset = preset_path / "indexPreset.json"
    if not index_preset.exists():
        writefile(index_preset, {"presetNames": ["start"], "preset": "start"})

    settings_path = data_path / "setting.json"
    if not settings_path.exists():
        data = {
            "dateTime": str(datetime.now()),
            "paths": {
                "homePath": str(src_path),
                "dataPath": str(data_path),
                "settingPath": str(settings_path),
                "presetPath": str(preset_path),
                "presetIndex": str(index_preset),
                "configPath": str(data_path / "config.json"),
            },
            "presetButton": ["12", "5", "3", "0", "1", "4", "9", "8"],
            "presetAxis": ["0", "5", "1"],
        }
        writefile(settings_path, data)

    radio_config = data_path / "radioConfig.json"
    if not radio_config.exists():
        writefile(
            radio_config,
            {
                "SERIAL_BAUD": 115200,
                "DISPLAY_REFRESH_S": 0.1,
                "DEFAULT_SEND_RATE": 30,
                "BINARY_MARKER": 0xAA,
                "DEFAULT_TX_POWER": 10,
                "SERIAL_TIMEOUT_S": 0.1,
                "MAX_SERIAL_ERRORS": 8,
                "DEBUG_EVERY_N_PACKETS": 30,
            },
        )


def scopri_assi(js, axis_names):
    print(f"\n  Mapping Assi per: {js.get_name()}")
    assi = {}
    for nome in axis_names:
        print(f"  Muovi {nome}...", end="", flush=True)
        baseline = [js.get_axis(i) for i in range(js.get_numaxes())]
        found = False
        t0 = time.time()
        while time.time() - t0 < 10 and not found:
            pygame.event.pump()
            for i in range(js.get_numaxes()):
                if abs(js.get_axis(i) - baseline[i]) > 0.5:
                    assi[nome] = i
                    print(f" OK (Asse {i})")
                    found = True
                    time.sleep(0.5)
                    break
        if not found:
            print(" Timeout!")
    return assi


def scopri_pulsanti(js, button_names):
    print("\n  Mapping Pulsanti...")
    btns = {}
    for nome in button_names:
        print(f"  Premi {nome}...", end="", flush=True)
        found = False
        t0 = time.time()
        while time.time() - t0 < 10 and not found:
            pygame.event.pump()
            for i in range(js.get_numbuttons()):
                if js.get_button(i):
                    btns[nome] = i
                    print(f" OK (Btn {i})")
                    found = True
                    time.sleep(0.5)
                    break
    return btns


def setUpVolante(js, button_names, axis_names, path):
    CLEAR()
    print(Fore.YELLOW + "Rilevamento hardware: " + js.get_name() + Style.RESET_ALL)

    config_path = Path(path)
    if config_path.exists() and input("Modificare i valori di default? (y/n): ").lower() != "y":
        print(Fore.GREEN + "Valori di default mantenuti." + Style.RESET_ALL)
        return

    data = {"button": {}, "axis": {}}

    print(Fore.CYAN + "\n--- CONFIGURAZIONE PULSANTI ---")
    data["button"] = scopri_pulsanti(js, button_names)

    print(Fore.CYAN + "\n--- CONFIGURAZIONE ASSI ---")
    data["axis"] = scopri_assi(js, axis_names)

    writefile(config_path, data)
    print(Fore.GREEN + "\nMappatura salvata con successo!" + Style.RESET_ALL)


# --- Funzioni di preset ---
def readfile(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def writefile(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def loadWorkSpace():
    setUpWorkSpace()
    data = readfile(_repo_src_path() / "data" / "setting.json")
    return data["paths"], data["presetButton"], data["presetAxis"]


def get_int_input(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
        except ValueError:
            pass
        print(f"Errore: inserire un numero tra {min_val} e {max_val}")


def presetMenu(presetIndex, presetPath, vel=50, angle=45):
    CLEAR()
    print(Fore.YELLOW + "Gestione PRESET" + Style.RESET_ALL)
    print("\t1. Salva attuale\n\t2. Crea nuovo\n\t3. Carica esistente")

    scelta = get_int_input("Opzione -> ", 1, 3)
    if scelta == 1:
        savePreset(presetIndex, presetPath, vel, angle)
        return reloadPreset(presetIndex, presetPath)
    if scelta == 2:
        createPreset(presetIndex, presetPath, vel, angle)
        return reloadPreset(presetIndex, presetPath)
    return loadPreset(presetIndex, presetPath)


def savePreset(presetIndex, presetPath, vel, angle):
    data = readfile(presetIndex)
    index = data["presetNames"].index(data["preset"])
    writefile(Path(presetPath) / f"preset{index}.json", {"maxVel": vel, "maxAngle": angle})
    print(Fore.GREEN + "Preset salvato correttamente!" + Style.RESET_ALL)


def createPreset(presetIndex, presetPath, vel, angle):
    CLEAR()
    data = readfile(presetIndex)
    names = data["presetNames"]

    name = ""
    while not name or name in names:
        name = input("Inserisci un nome univoco per il preset: ").lower().strip()

    names.append(name)

    if input("Vuoi inserire i valori manualmente? (y/n): ").lower() == "y":
        vel = get_int_input("Velocità (1-100): ", 1, 100)
        angle = get_int_input("Angolo (1-180): ", 1, 180)

    use_now = input("Usare subito questo preset? (y/n): ").lower() == "y"
    data["preset"] = name if use_now else data["preset"]
    writefile(presetIndex, data)
    writefile(Path(presetPath) / f"preset{len(names)-1}.json", {"maxVel": vel, "maxAngle": angle})


def loadPreset(presetIndex, presetPath):
    data = readfile(presetIndex)
    names = data["presetNames"]

    print(Fore.YELLOW + "Preset disponibili:")
    for i, name in enumerate(names):
        print(f"\t{i}. {name.capitalize()}")

    idx = get_int_input("\tScegli il numero del preset: ", 0, len(names) - 1)
    data["preset"] = names[idx]
    writefile(presetIndex, data)

    vel, angle = reloadPreset(presetIndex, presetPath)
    print(f"Caricato: {names[idx].upper()} (Vel: {vel}, Angolo: {angle})")
    return vel, angle


def reloadPreset(presetIndex, presetPath):
    data_idx = readfile(presetIndex)
    idx = data_idx["presetNames"].index(data_idx["preset"])
    preset_data = readfile(Path(presetPath) / f"preset{idx}.json")
    return preset_data["maxVel"], preset_data["maxAngle"]


def loadMap(path):
    with open(path, mode="r", encoding="utf-8") as f:
        dati = json.load(f)
        buttons = {k: int(v) for k, v in dati["button"].items()}
        axis = {k: int(v) for k, v in dati["axis"].items()}
    return buttons, axis


def CLEAR():
    os.system("cls" if os.name == "nt" else "clear")


def INIZIALISE(js):
    print(text2art("Squadra Corse", font="small"))
    print(Fore.YELLOW + "Controller connesso correttamente:" + Style.RESET_ALL)
    print(f"\t- Volante rilevato: {js.get_name()}")
    print(f"\t- Numero di pulsanti: {js.get_numbuttons()}")
    print(f"\t- Numero di assi: {js.get_numaxes()}")
    print(Fore.YELLOW + "\nCLICCARE PULSANTE PS PER ANDARE AVANTI" + Style.RESET_ALL)


def drawMenu():
    CLEAR()
    print(Fore.YELLOW + "Menu principale:" + Style.RESET_ALL)
    print("\tQUADRATO - Impostazioni veicolo")
    print("\tPS button - Menu/start/stop veicolo")
    print(Fore.RED + "\tX - Seleziona exit" + Style.RESET_ALL)
    print("Avvio del veicolo...")


def drawSettings(slx, opt):
    CLEAR()
    print("Impostazioni veicolo selezionate.")
    for idx, option in enumerate(opt, start=1):
        if idx - 1 == slx:
            print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
        else:
            print(f"\t{idx}. {option}")
    print("Premi CERCHIO per selezionare l'opzione.")
    print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)


def settingOption(value, position, max_val, min_val, var, id_opt, idValue, subdivision, opt):
    var = min(max_val, var + 1) if value > 0 and value > position else max(min_val, var - 1)
    position = value
    CLEAR()
    print("Impostazioni veicolo selezionate.")
    for idx, option in enumerate(opt, start=1):
        if idx - 1 == id_opt:
            print(Fore.YELLOW + f"\t> {idx}. {option} <" + Style.RESET_ALL)
            if id_opt == idValue:
                drawSettingOption(min_val, max_val, var, subdivision)
        else:
            print(f"\t{idx}. {option}")
    print("Premi CERCHIO per selezionare l'opzione.")
    print(Fore.RED + "Premi X per tornare al menu principale." + Style.RESET_ALL)
    return position, var


def drawSettingOption(min_val, max_val, var, subdivision):
    print(Fore.CYAN + f"\t   {min_val}" + Style.RESET_ALL, end=" ")
    print("|" * int(var / subdivision), end="")
    print("|" * (20 - int(var / subdivision)), end="")
    print(Fore.CYAN + f" {max_val} > {var}" + Style.RESET_ALL)


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if (crc & 0x8000) else (crc << 1)
            crc &= 0xFFFF
    return crc
