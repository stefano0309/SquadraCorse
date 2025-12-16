import socket
import json
import time
from Controller import PS4Controller

# Inizializza controller
controller = PS4Controller()

UDP_IP = "10.88.243.47"  # Server locale
UDP_PORT = 8080
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

running = True
while running:
    controller.update()

    # Crea il dizionario dei valori solo per quei tasti
    data = {
        "R2": controller.get_R2(),
        "L2": controller.get_L2(),
        "RX": controller.get_RX(),

        "X": controller.button_state.get(controller.button_mapping['X'], False)
    }

    message = json.dumps(data)
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
    
    # Chiudi se premuto X
    if controller.button_state.get(controller.button_mapping['X'], False):
        print("X premuto: chiusura client")
        break
    
    time.sleep(0.01)
