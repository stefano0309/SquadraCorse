import argparse
import sys
import time

import pygame
from colorama import Fore, Style, init

from src.objRadio import RadioController
from src.utils import (
    CLEAR,
    INIZIALISE,
    drawMenu,
    drawSettingOption,
    drawSettings,
    loadMap,
    loadWorkSpace,
    presetMenu,
    readfile,
    reloadPreset,
    setUpVolante,
    settingOption,
)

init(autoreset=True)

button_list = ["START", "EXIT", "SETTINGS", "UP", "DOWN", "SELECT", "RETRO_ON", "RETRO_OFF"]
axis_list = ["STEERING", "ACCELERATOR", "BRAKE"]
options_list = [
    "Regolazione massima velocità",
    "Regolazione angolo massimo sterzo",
    "Reset mappatura tasti",
    "Salva preset impostazioni",
]


class Controller:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.js = self._connect_first_joystick()

        self.paths, self.presetButton, self.presetAxis = loadWorkSpace()
        self.velocity, self.angle = presetMenu(self.paths["presetIndex"], self.paths["presetPath"])
        self.config = readfile(self.paths["dataPath"] + "/radioConfig.json")

        self.rc = RadioController()
        parser = argparse.ArgumentParser()
        parser.add_argument("port", nargs="?", default="COM13" if sys.platform == "win32" else "/dev/ttyUSB0")
        args = parser.parse_args()

        if not self.rc.connect(args.port, self.config["SERIAL_BAUD"]):
            print(Fore.RED + f"ERRORE: connessione seriale fallita su {args.port}" + Style.RESET_ALL)
            raise SystemExit(2)
        if not self.rc.handshake():
            print(Fore.RED + "ERRORE: handshake con TX fallito" + Style.RESET_ALL)
            raise SystemExit(3)

        setUpVolante(self.js, button_list, axis_list, self.paths["configPath"])
        self.buttons, self.axis = loadMap(self.paths["configPath"])
        if not self._validate_mapping():
            print(Fore.RED + "Mappatura non valida: rifai configurazione assi/pulsanti." + Style.RESET_ALL)
            raise SystemExit(4)

        CLEAR()
        INIZIALISE(self.js)

        self.running = True
        self.firstStart = True
        self.start = False
        self.settings = False
        self.selectItem = False
        self.retromarcia = False
        self.selected = 0
        self.position = 0
        self.option_selected = options_list

        self.deadzone = 0.05
        self.current_accel = 0.0
        self.current_steer = 0.0
        self.accel_rise_rate = 0.05
        self.accel_fall_rate = 0.08
        self.steer_rate = 0.10
        self.last_debug_print = 0.0

    def _connect_first_joystick(self):
        for _ in range(20):
            pygame.joystick.quit()
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                js = pygame.joystick.Joystick(0)
                js.init()
                return js
            time.sleep(0.1)
        print(Fore.RED + "ERRORE: Nessun controller trovato." + Style.RESET_ALL)
        pygame.quit()
        raise SystemExit(1)

    def _validate_mapping(self) -> bool:
        required_btn = set(button_list)
        required_axis = set(axis_list)
        if not required_btn.issubset(self.buttons) or not required_axis.issubset(self.axis):
            return False

        max_buttons = self.js.get_numbuttons()
        max_axes = self.js.get_numaxes()
        if max_axes <= 0:
            return False

        for name in required_btn:
            idx = self.buttons[name]
            if idx < 0 or idx >= max_buttons:
                return False
        for name in required_axis:
            idx = self.axis[name]
            if idx < 0 or idx >= max_axes:
                return False
        return True

    @staticmethod
    def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    def apply_deadzone(self, value: float) -> float:
        value = self._clamp(value)
        if abs(value) < self.deadzone:
            return 0.0
        scaled = (abs(value) - self.deadzone) / (1.0 - self.deadzone)
        return scaled if value > 0 else -scaled

    def normalize_trigger_axis(self, raw_value: float) -> float:
        raw_value = self._clamp(raw_value)
        return (raw_value + 1.0) / 2.0

    def smooth_to_target(self, current: float, target: float, rise: float, fall: float) -> float:
        if target > current:
            return min(target, current + rise)
        return max(target, current - fall)

    def _safe_get_axis(self, name: str) -> float:
        idx = self.axis.get(name, -1)
        if idx < 0 or idx >= self.js.get_numaxes():
            return 0.0
        return self.js.get_axis(idx)

    def _handle_device_event(self, event):
        if event.type == pygame.JOYDEVICEREMOVED:
            print(Fore.YELLOW + "Controller scollegato, attendo riconnessione..." + Style.RESET_ALL)
            self.start = False
        elif event.type == pygame.JOYDEVICEADDED:
            self.js = self._connect_first_joystick()
            print(Fore.GREEN + f"Controller riconnesso: {self.js.get_name()}" + Style.RESET_ALL)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self._handle_device_event(event)
                self.gestioneUscite(event)
                self.gestioneBottoni(event)
                self.gestioneAssi(event)

            pygame.event.pump()

            if self.start and not self.settings:
                self.invioDati()
                self.monitor_debug()
                time.sleep(0.02)

        if self.rc:
            self.rc.close()
        pygame.quit()

    def invioDati(self):
        steer_raw = self._safe_get_axis("STEERING")
        accel_raw = self._safe_get_axis("ACCELERATOR")
        brake_raw = self._safe_get_axis("BRAKE")

        steer_target = self.apply_deadzone(steer_raw)
        steer_limit = self.angle / 180.0
        steer_target *= steer_limit

        accel_target = self.normalize_trigger_axis(accel_raw)
        brake_target = self.normalize_trigger_axis(brake_raw)
        accel_target = max(0.0, accel_target - brake_target * 0.6)

        self.current_steer = self.smooth_to_target(self.current_steer, steer_target, self.steer_rate, self.steer_rate)
        self.current_accel = self.smooth_to_target(self.current_accel, accel_target, self.accel_rise_rate, self.accel_fall_rate)

        steer_byte = int((self.current_steer + 1.0) * 127.5)
        accel_byte = int(self.current_accel * 255 * (self.velocity / 100.0))
        brake_active = brake_target > 0.15

        self.rc.send_data(
            steer=max(0, min(255, steer_byte)),
            accel=max(0, min(255, accel_byte)),
            brake=brake_active,
            speed_sel=0,
            reverse=self.retromarcia,
            commands=0,
        )

    def monitor_debug(self):
        now = time.monotonic()
        for msg in self.rc.poll_messages():
            if "ERR" in msg or "FAIL" in msg or "NO_RADIO" in msg:
                print(Fore.RED + f"[TX/RX] {msg}" + Style.RESET_ALL)

        if now - self.last_debug_print >= 1.0:
            self.last_debug_print = now
            fail_ratio = (self.rc.tx_fail / max(1, self.rc.tx_count)) * 100
            print(Fore.CYAN + f"[DEBUG] sent={self.rc.tx_count} fail={self.rc.tx_fail} ({fail_ratio:.1f}%)" + Style.RESET_ALL)

        if self.rc.has_serial_fault():
            print(Fore.RED + "[ERRORE] Troppi errori seriali consecutivi, stop sicurezza." + Style.RESET_ALL)
            self.start = False

    def gestioneUscite(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False

    def gestioneBottoni(self, event):
        if event.type != pygame.JOYBUTTONDOWN:
            return

        if event.button == self.buttons["RETRO_ON"]:
            self.retromarcia = True
            print(Fore.CYAN + "RETROMARCIA: ON" + Style.RESET_ALL)
        elif event.button == self.buttons["RETRO_OFF"]:
            self.retromarcia = False
            print(Fore.CYAN + "RETROMARCIA: OFF" + Style.RESET_ALL)
        elif event.button == self.buttons["START"]:
            self.gestioneInizio()
        elif event.button == self.buttons["EXIT"]:
            self.gestioneUsciteBottoni()

        if self.settings:
            self.gestioneBottoniImpostazioni(event)
        elif event.button == self.buttons["SETTINGS"] and not self.start:
            self.gestioneImpostazioni()

    def gestioneAssi(self, event):
        if event.type != pygame.JOYAXISMOTION:
            return

        if self.settings and self.selectItem:
            if self.selected == 0:
                self.position, self.velocity = settingOption(event.value, self.position, 100, 1, self.velocity, self.selected, 0, 5, self.option_selected)
            elif self.selected == 1:
                self.position, self.angle = settingOption(event.value, self.position, 180, 1, self.angle, self.selected, 1, 9, self.option_selected)

    def gestioneInizio(self):
        if self.firstStart:
            CLEAR()
            self.firstStart = False
            self.start = True
            drawMenu()
        else:
            self.start = not self.start
            drawMenu()

    def gestioneUsciteBottoni(self):
        if not self.start and not self.settings:
            self.running = False
        if self.settings:
            self.settings = False
            self.selectItem = False
            drawMenu()

    def gestioneImpostazioni(self):
        self.settings = True
        self.selected = 0
        drawSettings(self.selected, self.option_selected)

    def gestioneBottoniImpostazioni(self, event):
        if event.button == self.buttons["UP"]:
            self.selectItem = False
            self.selected = max(0, self.selected - 1)
            drawSettings(self.selected, self.option_selected)
        elif event.button == self.buttons["DOWN"]:
            self.selectItem = False
            self.selected = min(len(self.option_selected) - 1, self.selected + 1)
            drawSettings(self.selected, self.option_selected)
        elif event.button == self.buttons["SELECT"]:
            self.gestioneOpzioniImpostazioni()

    def gestioneOpzioniImpostazioni(self):
        if self.selectItem:
            self.selectItem = False
            drawSettings(self.selected, self.option_selected)
            return

        self.selectItem = True
        CLEAR()
        if self.selected == 2:
            setUpVolante(self.js, button_list, axis_list, self.paths["configPath"])
            self.buttons, self.axis = loadMap(self.paths["configPath"])
            self.settings = False
            drawMenu()
        elif self.selected == 3:
            presetMenu(self.paths["presetIndex"], self.paths["presetPath"], self.velocity, self.angle)
            self.velocity, self.angle = reloadPreset(self.paths["presetIndex"], self.paths["presetPath"])
            self.selectItem = False
            drawSettings(self.selected, self.option_selected)
        else:
            drawSettings(self.selected, self.option_selected)
            if self.selected == 0:
                drawSettingOption(1, 100, self.velocity, 5)
            if self.selected == 1:
                drawSettingOption(1, 180, self.angle, 9)
