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
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);

  radio.openReadingPipe(0, address);
  radio.startListening();

  Serial.println("RX pronto");
}

void loop() {
  if (radio.available()) {
    char buf[32];
    radio.read(buf, sizeof(buf));
    buf[31] = 0;
    Serial.println(buf);
  }
}
