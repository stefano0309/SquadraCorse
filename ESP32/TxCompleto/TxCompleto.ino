/*
 * TxCompleto.ino — Trasmissione Squadra Corse (robust + paced link)
 */

#include <SPI.h>
#include <LoRa.h>
#include <nRF24L01.h>
#include <RF24.h>

#define LORA_SCK    18
#define LORA_MISO   19
#define LORA_MOSI   23
#define LORA_CS      5
#define LORA_RST    21

RF24 radio(2, 4);
const byte nrfAddress[6] = "00001";

#define PACKET_SIZE            7
#define USB_FRAME_SIZE         6
#define BINARY_MARKER       0xAA
#define PROBE_INTERVAL_MS   5000
#define STATS_INTERVAL_MS   5000
#define RX_USB_TIMEOUT_MS    350
#define DEBUG_SERIAL        false

int loraTxPower = 20;
int sendRate = 45;

enum RadioType { RADIO_NONE, RADIO_LORA, RADIO_NRF24 };
RadioType activeRadio = RADIO_NONE;

unsigned long lastProbeMs = 0;
unsigned long lastStatsMs = 0;
unsigned long lastSendMs = 0;
unsigned long lastUsbFrameMs = 0;

uint8_t txSeq = 0;
uint8_t latestPayload[3] = {128, 0, 0};
bool havePayload = false;

uint32_t statSentOk = 0;
uint32_t statSentFail = 0;
uint32_t statCrcErrUsb = 0;

uint8_t serialBuf[64];
uint8_t serialCount = 0;

uint16_t crc16_ccitt(const uint8_t *data, uint8_t len) {
  uint16_t crc = 0xFFFF;
  for (uint8_t i = 0; i < len; i++) {
    crc ^= (uint16_t)data[i] << 8;
    for (uint8_t j = 0; j < 8; j++) crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : crc << 1;
  }
  return crc;
}

bool initLoRa() {
  SPI.end();
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
  LoRa.setPins(LORA_CS, LORA_RST, -1);
  if (!LoRa.begin(433E6)) return false;
  LoRa.setSpreadingFactor(8);
  LoRa.setSignalBandwidth(250E3);
  LoRa.setCodingRate4(6);
  LoRa.setPreambleLength(8);
  LoRa.setSyncWord(0x12);
  LoRa.enableCrc();
  LoRa.setTxPower(loraTxPower);
  return true;
}

bool initNRF24() {
  SPI.end();
  SPI.begin();
  SPI.setClockDivider(SPI_CLOCK_DIV16);
  if (!radio.begin()) return false;
  radio.setChannel(73);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);
  radio.setPayloadSize(PACKET_SIZE);
  radio.setAutoAck(false);
  radio.openWritingPipe(nrfAddress);
  radio.stopListening();
  return true;
}

const char *radioName() {
  switch (activeRadio) {
    case RADIO_LORA: return "LORA";
    case RADIO_NRF24: return "NRF24";
    default: return "NONE";
  }
}

RadioType detectRadio() {
  if (initLoRa()) return RADIO_LORA;
  if (initNRF24()) return RADIO_NRF24;
  return RADIO_NONE;
}

void probeRadio() {
  RadioType prev = activeRadio;
  bool stillAlive = false;

  if (prev == RADIO_LORA) stillAlive = initLoRa();
  else if (prev == RADIO_NRF24) stillAlive = initNRF24();

  if (stillAlive) return;

  RadioType found = detectRadio();
  activeRadio = found;
  if (found != prev) {
    Serial.print("MODULE_CHANGED ");
    Serial.println(radioName());
  }
}

bool transmitPacket(const uint8_t *payload3) {
  uint8_t pkt[PACKET_SIZE];
  pkt[0] = 0xA2;  // protocol marker compact v2
  memcpy(pkt + 1, payload3, 3);
  pkt[4] = txSeq++;

  uint16_t crc = crc16_ccitt(pkt, 5);
  pkt[5] = (crc >> 8) & 0xFF;
  pkt[6] = crc & 0xFF;

  if (activeRadio == RADIO_LORA) {
    LoRa.beginPacket();
    LoRa.write(pkt, PACKET_SIZE);
    return LoRa.endPacket(false) == 1;
  }
  if (activeRadio == RADIO_NRF24) return radio.write(pkt, PACKET_SIZE);
  return false;
}

void sendStatus() {
  Serial.print("STATUS ");
  Serial.print(radioName());
  Serial.print(" ");
  Serial.print(sendRate);
  Serial.print(" SENT=");
  Serial.print(statSentOk);
  Serial.print(" FAIL=");
  Serial.println(statSentFail);
}

void handleCommand(String cmd) {
  cmd.trim();
  if (cmd == "HANDSHAKE") {
    Serial.print("ACK ");
    Serial.print(radioName());
    Serial.print(" ");
    Serial.println(sendRate);
  } else if (cmd.startsWith("SET TXPOWER ")) {
    int v = cmd.substring(12).toInt();
    if (v >= 2 && v <= 20) {
      loraTxPower = v;
      if (activeRadio == RADIO_LORA) LoRa.setTxPower(loraTxPower);
      Serial.println("OK");
    } else Serial.println("ERR TXPOWER_RANGE");
  } else if (cmd.startsWith("SET SENDRATE ")) {
    int v = cmd.substring(13).toInt();
    if (v >= 5 && v <= 100) {
      sendRate = v;
      Serial.println("OK");
    } else Serial.println("ERR SENDRATE_RANGE");
  } else if (cmd == "STATUS") {
    sendStatus();
  } else {
    Serial.println("ERR UNKNOWN_CMD");
  }
}

void _pushSerialByte(uint8_t b) {
  if (serialCount < sizeof(serialBuf)) serialBuf[serialCount++] = b;
  else serialCount = 0;
}

void _consumeFrameAtStart() {
  if (serialCount < USB_FRAME_SIZE) return;
  uint16_t rxCrc = ((uint16_t)serialBuf[4] << 8) | serialBuf[5];
  uint16_t calcCrc = crc16_ccitt(serialBuf + 1, 3);
  if (rxCrc == calcCrc) {
    latestPayload[0] = serialBuf[1];
    latestPayload[1] = serialBuf[2];
    latestPayload[2] = serialBuf[3];
    havePayload = true;
    lastUsbFrameMs = millis();
    for (uint8_t i = USB_FRAME_SIZE; i < serialCount; i++) serialBuf[i - USB_FRAME_SIZE] = serialBuf[i];
    serialCount -= USB_FRAME_SIZE;
    return;
  }

  statCrcErrUsb++;
  for (uint8_t i = 1; i < serialCount; i++) serialBuf[i - 1] = serialBuf[i];
  serialCount -= 1;
}

void handleUsbInput() {
  while (Serial.available() > 0) {
    uint8_t b = (uint8_t)Serial.read();
    _pushSerialByte(b);

    bool progressed = true;
    while (progressed) {
      progressed = false;

      if (serialCount == 0) break;

      if (serialBuf[0] == BINARY_MARKER) {
        if (serialCount < USB_FRAME_SIZE) {
          // Attendo frame binario completo
          break;
        }
        _consumeFrameAtStart();
        progressed = true;
        continue;
      }

      // Comandi testuali (es. HANDSHAKE + newline)
      if (serialBuf[0] >= 32 && serialBuf[0] <= 126) {
        int nl = -1;
        for (uint8_t i = 0; i < serialCount; i++) {
          if (serialBuf[i] == '\n') {
            nl = i;
            break;
          }
        }

        if (nl < 0) {
          // Riga non completa: non scarto nulla, aspetto altri byte
          // salvo protezione overflow se una riga non termina mai
          if (serialCount >= sizeof(serialBuf) - 1) serialCount = 0;
          break;
        }

        String cmd = "";
        for (int i = 0; i < nl; i++) cmd += (char)serialBuf[i];
        handleCommand(cmd);

        for (uint8_t i = nl + 1; i < serialCount; i++) serialBuf[i - (nl + 1)] = serialBuf[i];
        serialCount -= (uint8_t)(nl + 1);
        progressed = true;
        continue;
      }

      // Byte non valido in testa buffer: scarta solo 1 byte e ritenta sync
      for (uint8_t i = 1; i < serialCount; i++) serialBuf[i - 1] = serialBuf[i];
      serialCount -= 1;
      progressed = true;
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  SPI.begin();

  activeRadio = detectRadio();
  Serial.println("READY");
}

void loop() {
  unsigned long now = millis();

  if (activeRadio == RADIO_NONE && (now - lastProbeMs >= PROBE_INTERVAL_MS)) {
    lastProbeMs = now;
    probeRadio();
  }

  handleUsbInput();

  if (havePayload && (now - lastUsbFrameMs > RX_USB_TIMEOUT_MS)) {
    // Mantieni sterzo e direzione; taglia solo accelerazione per sicurezza morbida.
    latestPayload[1] = 0;
    latestPayload[2] |= (1 << 3);
  }

  unsigned long intervalMs = (sendRate > 0) ? (1000UL / (unsigned long)sendRate) : 30;
  if (havePayload && now - lastSendMs >= intervalMs) {
    lastSendMs = now;
    if (activeRadio == RADIO_NONE) statSentFail++;
    else if (transmitPacket(latestPayload)) statSentOk++;
    else statSentFail++;
  }

  if (DEBUG_SERIAL && now - lastStatsMs >= STATS_INTERVAL_MS) {
    lastStatsMs = now;
    Serial.print("TX_STATS ok=");
    Serial.print(statSentOk);
    Serial.print(" fail=");
    Serial.print(statSentFail);
    Serial.print(" usb_crc=");
    Serial.println(statCrcErrUsb);
  }
}
