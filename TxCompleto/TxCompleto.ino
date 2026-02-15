/*
 * TxCompleto.ino — Trasmissione Squadra Corse
 *
 * Pacchetto radio 10 byte:
 *   [0-3] Token "VAL1"
 *   [4]   Sterzo       (0-255, 128 = centro)
 *   [5]   Accelerazione(0-255)
 *   [6]   Freno        (0-255)
 *   [7]   speed_sel:4 | reverse:1 | comandi:3
 *   [8-9] CRC-16 CCITT  (big-endian, su byte 0-7)
 *
 * Protocollo USB  (testo, '\n'-terminated):
 *   HANDSHAKE          → ACK <modulo> <rate> [<txpower>]
 *   SET TXPOWER <v>    → OK | ERR …
 *   SET SENDRATE <v>   → OK | ERR …
 *   STATUS             → STATUS <modulo> <rate> [<txpower>]
 *
 * Messaggi asincroni dal TX → PC:
 *   MODULE_CHANGED <modulo> [<txpower>]
 *
 * Hot-swap hardware: il modulo viene sostituito fisicamente.
 * Il TX ri-proba periodicamente e segnala il cambio via USB.
 *
 * Protocollo USB  (binario, 7 byte):
 *   0xAA | sterzo | accel | freno | misc | CRC-16 hi | CRC-16 lo
 */

#include <SPI.h>

// ==================== LoRa ====================
#include <LoRa.h>
#define LORA_SCK    18
#define LORA_MISO   19
#define LORA_MOSI   23
#define LORA_CS      5
#define LORA_RST    21

// ==================== nRF24 ====================
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(2, 4);                       // CE=2, CSN=4
const byte nrfAddress[6] = "00001";

// ================ CONFIGURAZIONE ================
#define PACKET_SIZE        10
#define USB_FRAME_SIZE      7
#define BINARY_MARKER    0xAA
#define PROBE_INTERVAL_MS 2000          // ogni 2 s controlla se il modulo è cambiato

int  loraTxPower  = 20;                 // dBm  (2 – 20)
int  sendRate     = 20;                 // Hz

// ==================== STATO ====================
enum RadioType { RADIO_NONE, RADIO_LORA, RADIO_NRF24 };
RadioType activeRadio = RADIO_NONE;
unsigned long lastProbeMs = 0;

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
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(250E3);
  LoRa.setCodingRate4(5);
  LoRa.setPreambleLength(6);
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

// ========== DETECT / PROBE ==========
// Prova a trovare un modulo. Restituisce il tipo trovato.
RadioType detectRadio() {
  if (initLoRa())  return RADIO_LORA;
  if (initNRF24()) return RADIO_NRF24;
  return RADIO_NONE;
}

// Chiamata periodica: controlla se il modulo HW è cambiato.
void probeRadio() {
  RadioType prev = activeRadio;

  // Prima controlla se il modulo attuale è ancora presente
  bool stillAlive = false;
  if (prev == RADIO_LORA) {
    // LoRa: prova a ri-inizializzare
    stillAlive = initLoRa();
  } else if (prev == RADIO_NRF24) {
    stillAlive = initNRF24();
  }

  if (stillAlive) {
    activeRadio = prev;  // tutto OK, modulo invariato
    return;
  }

  // Modulo precedente non risponde: prova l'altro
  RadioType found = detectRadio();
  activeRadio = found;

  if (found != prev) {
    // Segnala il cambio via USB
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
bool transmitPacket(const uint8_t *payload4) {
  uint8_t pkt[PACKET_SIZE];
  pkt[0] = 'V'; pkt[1] = 'A'; pkt[2] = 'L'; pkt[3] = '1';
  memcpy(pkt + 4, payload4, 4);
  uint16_t crc = crc16_ccitt(pkt, 8);
  pkt[8] = (crc >> 8) & 0xFF;
  pkt[9] =  crc       & 0xFF;

  if (activeRadio == RADIO_LORA) {
    LoRa.beginPacket(true);
    LoRa.write(pkt, PACKET_SIZE);
    LoRa.endPacket(true);
    return true;
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
  Serial.println();
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
    if (v >= 1 && v <= 100) {
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
  // ── Probe periodico modulo HW ──
  unsigned long now = millis();
  if (now - lastProbeMs >= PROBE_INTERVAL_MS) {
    lastProbeMs = now;
    probeRadio();
  }

  // ── Seriale USB ──
  if (Serial.available() == 0) { delay(1); return; }

  uint8_t first = Serial.peek();

  // ---------- frame binario ----------
  if (first == BINARY_MARKER) {
    if (Serial.available() < USB_FRAME_SIZE) { delay(1); return; }

    uint8_t frame[USB_FRAME_SIZE];
    Serial.readBytes(frame, USB_FRAME_SIZE);

    uint16_t rxCrc   = ((uint16_t)frame[5] << 8) | frame[6];
    uint16_t calcCrc = crc16_ccitt(frame + 1, 4);

    if (rxCrc != calcCrc) {
      Serial.println("CRC_ERR");
      while (Serial.available()) Serial.read();
      return;
    }

    if (activeRadio == RADIO_NONE) {
      Serial.println("NO_RADIO");
      return;
    }

    bool ok = transmitPacket(frame + 1);
    if (!ok) Serial.println("TX_FAIL");
  }
  // ---------- comando testo ----------
  else {
    String cmd = Serial.readStringUntil('\n');
    handleCommand(cmd);
  }
}