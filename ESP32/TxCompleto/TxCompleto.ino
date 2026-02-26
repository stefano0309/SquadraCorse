/*
 * TxCompleto.ino — Trasmissione Squadra Corse (robust link)
 *
 * Pacchetto radio 10 byte:
 *   [0-3] Token "VAL2"
 *   [4]   Sterzo       (0-255, 128 = centro)
 *   [5]   Accelerazione(0-255)
 *   [6]   speed_sel:4 | brake:1 | reverse:1 | comandi:2
 *   [7]   Sequence ID  (0-255)
 *   [8-9] CRC-16 CCITT (big-endian, su byte 0-7)
 *
 * Protocollo USB (binario, 6 byte):
 *   0xAA | sterzo | accel | misc | CRC16_hi | CRC16_lo
 */

#include <SPI.h>
#include <LoRa.h>
#include <nRF24L01.h>
#include <RF24.h>

// ==================== LoRa ====================
#define LORA_SCK    18
#define LORA_MISO   19
#define LORA_MOSI   23
#define LORA_CS      5
#define LORA_RST    21

// ==================== nRF24 ====================
RF24 radio(2, 4);                       // CE=2, CSN=4
const byte nrfAddress[6] = "00001";

// ================ CONFIGURAZIONE ================
#define PACKET_SIZE          10
#define USB_FRAME_SIZE        6
#define BINARY_MARKER      0xAA
#define PROBE_INTERVAL_MS  2000
#define STATS_INTERVAL_MS  1000

int  loraTxPower  = 20;                 // dBm 2-20
int  sendRate     = 30;                 // Hz

// ==================== STATO ====================
enum RadioType { RADIO_NONE, RADIO_LORA, RADIO_NRF24 };
RadioType activeRadio = RADIO_NONE;
unsigned long lastProbeMs = 0;
unsigned long lastStatsMs = 0;
uint8_t txSeq = 0;

uint32_t statSentOk = 0;
uint32_t statSentFail = 0;
uint32_t statCrcErrUsb = 0;

// ==================== CRC-16 ====================
uint16_t crc16_ccitt(const uint8_t *data, uint8_t len) {
  uint16_t crc = 0xFFFF;
  for (uint8_t i = 0; i < len; i++) {
    crc ^= (uint16_t)data[i] << 8;
    for (uint8_t j = 0; j < 8; j++)
      crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : crc << 1;
  }
  return crc;
}

// ============== INIT MODULI RADIO ==============
bool initLoRa() {
  SPI.end();
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
  LoRa.setPins(LORA_CS, LORA_RST, -1);
  if (!LoRa.begin(433E6)) return false;

  // Profilo robustezza/link budget per ~70m affidabili
  LoRa.setSpreadingFactor(9);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(8);
  LoRa.setPreambleLength(10);
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
  radio.setAutoAck(true);
  radio.setRetries(5, 15); // ~2ms * 5 max retry window
  radio.openWritingPipe(nrfAddress);
  radio.stopListening();
  return true;
}

const char *radioName() {
  switch (activeRadio) {
    case RADIO_LORA:  return "LORA";
    case RADIO_NRF24: return "NRF24";
    default:          return "NONE";
  }
}

RadioType detectRadio() {
  if (initLoRa())  return RADIO_LORA;
  if (initNRF24()) return RADIO_NRF24;
  return RADIO_NONE;
}

void probeRadio() {
  RadioType prev = activeRadio;

  bool stillAlive = false;
  if (prev == RADIO_LORA) {
    stillAlive = initLoRa();
  } else if (prev == RADIO_NRF24) {
    stillAlive = initNRF24();
  }

  if (stillAlive) {
    activeRadio = prev;
    return;
  }

  RadioType found = detectRadio();
  activeRadio = found;

  if (found != prev) {
    Serial.print("MODULE_CHANGED ");
    Serial.print(radioName());
    if (found == RADIO_LORA) {
      Serial.print(" ");
      Serial.print(loraTxPower);
    }
    Serial.println();
  }
}

// ========== COSTRUZIONE + TRASMISSIONE ==========
bool transmitPacket(const uint8_t *payload3) {
  uint8_t pkt[PACKET_SIZE];
  pkt[0] = 'V'; pkt[1] = 'A'; pkt[2] = 'L'; pkt[3] = '2';
  memcpy(pkt + 4, payload3, 3);
  pkt[7] = txSeq++;

  uint16_t crc = crc16_ccitt(pkt, 8);
  pkt[8] = (crc >> 8) & 0xFF;
  pkt[9] = crc & 0xFF;

  if (activeRadio == RADIO_LORA) {
    LoRa.beginPacket();
    LoRa.write(pkt, PACKET_SIZE);
    int ok = LoRa.endPacket(true);
    return ok == 1;
  }

  if (activeRadio == RADIO_NRF24) {
    return radio.write(pkt, PACKET_SIZE);
  }
  return false;
}

// ============ GESTIONE COMANDI TESTO ============
void sendStatus() {
  Serial.print("STATUS ");
  Serial.print(radioName());
  Serial.print(" ");
  Serial.print(sendRate);
  if (activeRadio == RADIO_LORA) {
    Serial.print(" ");
    Serial.print(loraTxPower);
  }
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
    Serial.print(sendRate);
    if (activeRadio == RADIO_LORA) {
      Serial.print(" ");
      Serial.print(loraTxPower);
    }
    Serial.println();
  }
  else if (cmd.startsWith("SET TXPOWER ")) {
    int v = cmd.substring(12).toInt();
    if (v >= 2 && v <= 20) {
      loraTxPower = v;
      if (activeRadio == RADIO_LORA) LoRa.setTxPower(loraTxPower);
      Serial.println("OK");
    } else {
      Serial.println("ERR TXPOWER_RANGE");
    }
  }
  else if (cmd.startsWith("SET SENDRATE ")) {
    int v = cmd.substring(13).toInt();
    if (v >= 1 && v <= 120) {
      sendRate = v;
      Serial.println("OK");
    } else {
      Serial.println("ERR SENDRATE_RANGE");
    }
  }
  else if (cmd == "STATUS") {
    sendStatus();
  }
  else {
    Serial.println("ERR UNKNOWN_CMD");
  }
}

// ======================== SETUP ========================
void setup() {
  Serial.begin(115200);
  delay(1000);
  SPI.begin();

  activeRadio = detectRadio();
  Serial.println("READY");
}

// ======================== LOOP =========================
void loop() {
  unsigned long now = millis();

  if (now - lastProbeMs >= PROBE_INTERVAL_MS) {
    lastProbeMs = now;
    probeRadio();
  }

  if (now - lastStatsMs >= STATS_INTERVAL_MS) {
    lastStatsMs = now;
    Serial.print("TX_STATS ok=");
    Serial.print(statSentOk);
    Serial.print(" fail=");
    Serial.print(statSentFail);
    Serial.print(" usb_crc=");
    Serial.println(statCrcErrUsb);
  }

  if (Serial.available() == 0) {
    delay(1);
    return;
  }

  uint8_t first = Serial.peek();

  if (first == BINARY_MARKER) {
    if (Serial.available() < USB_FRAME_SIZE) {
      delay(1);
      return;
    }

    uint8_t frame[USB_FRAME_SIZE];
    Serial.readBytes(frame, USB_FRAME_SIZE);

    uint16_t rxCrc = ((uint16_t)frame[4] << 8) | frame[5];
    uint16_t calcCrc = crc16_ccitt(frame + 1, 3);

    if (rxCrc != calcCrc) {
      statCrcErrUsb++;
      Serial.println("CRC_ERR");
      return;
    }

    if (activeRadio == RADIO_NONE) {
      statSentFail++;
      Serial.println("NO_RADIO");
      return;
    }

    bool ok = transmitPacket(frame + 1);
    if (ok) {
      statSentOk++;
    } else {
      statSentFail++;
      Serial.println("TX_FAIL");
    }
  }
  else {
    String cmd = Serial.readStringUntil('\n');
    handleCommand(cmd);
  }
}
