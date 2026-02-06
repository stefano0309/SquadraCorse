#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(2, 4);
const byte address[6] = "00001";

void setup() {
  Serial.begin(115200);

  SPI.begin();
  SPI.setClockDivider(SPI_CLOCK_DIV16); // <-- QUI

  if (!radio.begin()) {
    Serial.println("NRF KO");
    while (1);
  }

  radio.setChannel(40);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);

  radio.openWritingPipe(address);
  radio.stopListening();

  Serial.println("TX pronto");
}

void loop() {
  const char msg[] = "1234567890123456789012345678901";
  bool ok = radio.write(msg, sizeof(msg));
  Serial.println(ok ? "OK" : "FAIL");
  delay(100);
}
