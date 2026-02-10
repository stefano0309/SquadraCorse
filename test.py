import time
import board
import busio
import digitalio
from circuitpython_nrf24l01.rf24 import RF24

# Configurazione Pin (Adatta i pin CE e CSN se necessario)
# Sul Raspberry Pi standard: CE=GPIO22, CSN=GPIO8 (CE0)
ce_pin = digitalio.DigitalInOut(board.D22)
csn_pin = digitalio.DigitalInOut(board.D8)

# Configurazione SPI
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Inizializzazione Radio
radio = RF24(spi, csn_pin, ce_pin)

# Configurazione identica allo script C++
address = b"00001" # L'indirizzo deve essere in formato bytes
radio.channel = 40
radio.pa_level = -0 # Corrisponde a RF24_PA_MAX (0 dBm)
radio.data_rate = 250 # Corrisponde a RF24_250KBPS

# Configurazione Pipe di Scrittura
radio.open_tx_pipe(address)
radio.listen = False # Equivale a stopListening()

print("TX pronto su Raspberry Pi")

def loop():
    # Messaggio di 31 caratteri (come nel tuo codice originale)
    msg = b"1234567890123456789012345678901"
    
    while True:
        # radio.send() restituisce True se riceve l'ACK
        result = radio.send(msg)
        
        if result:
            print("OK")
        else:
            print("FAIL")
            
        time.sleep(0.1) # Delay di 100ms

if __name__ == "__main__":
    try:
        loop()
    except KeyboardInterrupt:
        print("\nChiusura programma.")