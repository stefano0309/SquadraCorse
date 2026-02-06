#include <SPI.h>
#include <LoRa.h>

// Pin LoRa
#define LORA_CS   5
#define LORA_RST  21
#define LORA_IRQ  26

#define LORA_FREQ 433E6

void setup() {
  Serial.begin(115200);
  while (!Serial);

  LoRa.setPins(LORA_CS, LORA_RST, LORA_IRQ);

  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println("Errore inizializzazione LoRa!");
    while (1);
  }

  Serial.println("Trasmettitore LoRa pronto");

  // Parametri LoRa
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(5);
  LoRa.setTxPower(17);
}

void loop() {
  // Genera valori casuali
  uint8_t direzione = random(0, 256);
  uint8_t velocita  = random(0, 256);
  uint8_t freno     = random(0, 256);

  LoRa.beginPacket();
  LoRa.write(direzione);
  LoRa.write(velocita);
  LoRa.write(freno);
  LoRa.endPacket();

  Serial.print("Inviato -> ");
  Serial.print(direzione); Serial.print(" ");
  Serial.print(velocita); Serial.print(" ");
  Serial.println(freno);

  delay(10); // circa 10 pacchetti al secondo
}
