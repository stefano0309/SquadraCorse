import time
import board
import busio
import digitalio
from circuitpython_nrf24l01.rf24 import RF24

# Configurazione SPI e Pin (Usa SCLK per evitare errori di attributo)
spi = busio.SPI(board.SCLK, MOSI=board.MOSI, MISO=board.MISO)
ce_pin = digitalio.DigitalInOut(board.D22)
csn_pin = digitalio.DigitalInOut(board.D8)

# Inizializzazione Radio
radio = RF24(spi, csn_pin, ce_pin)

# [cite_start]Configurazione identica al tuo C++ [cite: 1, 2, 3]
radio.channel = 40                 # radio.setChannel(40)
radio.pa_level = 0                 # radio.setPALevel(RF24_PA_MAX)
radio.data_rate = 250              # radio.setDataRate(RF24_250KBPS)
radio.open_tx_pipe(b"00001")       # const byte address[6] = "00001"
radio.listen = False               # radio.stopListening()

print("TX pronto: invio dati all'ESP32...")

# [cite_start]Messaggio di 31 caratteri [cite: 4]
msg = b"1234567890123456789012345678901"

try:
    while True:
        result = radio.send(msg)
        if result:
            print("Inviato: OK")
        else:
            print("Inviato: FAIL (nessun ACK dall'ESP32)")
        time.sleep(0.1) # delay(100)
except KeyboardInterrupt:
    print("\nChiusura...")