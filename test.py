import time
import board
import busio
import digitalio
from circuitpython_nrf24l01.rf24 import RF24

# 1. Setup SPI con nomi dei pin più compatibili
# Usiamo SCLK al posto di SCK per evitare l'AttributeError
spi = busio.SPI(board.SCLK, MOSI=board.MOSI, MISO=board.MISO)

# 2. Setup Pin CE e CSN (come nel tuo script originale [cite: 1])
ce_pin = digitalio.DigitalInOut(board.D22)
csn_pin = digitalio.DigitalInOut(board.D8)

# 3. Inizializzazione Radio
radio = RF24(spi, csn_pin, ce_pin)

# 4. Configurazione speculare all'ESP32 
radio.channel = 40              # radio.setChannel(40)
radio.pa_level = 0               # radio.setPALevel(RF24_PA_MAX)
radio.data_rate = 250            # radio.setDataRate(RF24_250KBPS)
radio.open_tx_pipe(b"00001")     # radio.openWritingPipe("00001") [cite: 1]
radio.listen = False             # radio.stopListening() [cite: 3]

print("TX pronto su Raspberry Pi")

# 5. Loop di invio [cite: 4]
msg = b"1234567890123456789012345678901" # Messaggio di 31 byte [cite: 4]

while True:
    result = radio.send(msg)
    if result:
        print("OK")
    else:
        print("FAIL")
    
    time.sleep(0.1) # delay(100) [cite: 4]