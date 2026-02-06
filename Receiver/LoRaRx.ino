#include <SPI.h>
#include <LoRa.h>

// Pin LoRa
#define LORA_CS   5
#define LORA_RST  21
#define LORA_IRQ  26

#define LORA_FREQ 433E6

unsigned long lastPrintTime = 0;
int packetCount = 0;

// Ultimi valori di segnale
int lastRssi = 0;
float lastSnr = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  LoRa.setPins(LORA_CS, LORA_RST, LORA_IRQ);

  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println("Errore inizializzazione LoRa!");
    while (1);
  }

  Serial.println("Ricevitore LoRa pronto");
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // Salva RSSI e SNR dell'ultimo pacchetto ricevuto
    lastRssi = LoRa.packetRssi();
    lastSnr  = LoRa.packetSnr();

    // Leggi 3 byte del comando se disponibili
    if (LoRa.available() >= 3) {
      LoRa.read(); // direzione
      LoRa.read(); // velocità
      LoRa.read(); // freno
      packetCount++;
    }
  }

  // Stampa riepilogo ogni secondo
  if (millis() - lastPrintTime >= 1000) {
    Serial.print("Pkt/s: ");
    Serial.print(packetCount);

    Serial.print(" | RSSI: ");
    Serial.print(lastRssi);
    Serial.print(" dBm");

    Serial.print(" | SNR: ");
    Serial.print(lastSnr, 1);
    Serial.println(" dB");

    packetCount = 0;
    lastPrintTime = millis();
  }
}
