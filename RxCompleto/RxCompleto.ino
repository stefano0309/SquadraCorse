/*
 * RxCompleto.ino — Ricezione Squadra Corse
 *
 * Pacchetto radio 9 byte:
 *   [0-3] Token "VAL1"
 *   [4]   Sterzo        (0-255, 128 = centro)
 *   [5]   Accelerazione (0-255)
 *   [6]   speed_sel:4 | brake:1 | reverse:1 | comandi:2
 *   [7-8] CRC-16 CCITT  (big-endian, su byte 0-6)
 *
 * Hot-swap hardware: il modulo viene sostituito fisicamente.
 * Il RX ri-proba periodicamente (ogni PROBE_INTERVAL_MS) e
 * si adatta automaticamente al modulo presente.
 */

#include <SPI.h>
#include <ESP32Servo.h>

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

// ==================== Servo ====================
#define SERVO_PIN       26
const int SERVO_CENTER = 90;

// ==================== Motore ====================
#define PWM_PIN         25
#define DIR_FWD_PIN     33
#define DIR_REV_PIN     32
#define PWM_FREQ      1000
#define PWM_RES          8      // 8 bit → 0-255

// ============== CONFIGURAZIONE ==============
#define STEER_ANGLE_MAX     45
#define MAX_SPEEDS           6
#define REVERSE_MULTIPLIER   0.5f
#define DEADZONE             0.08f
#define FAILSAFE_MS          500
#define PROBE_INTERVAL_MS   2000        // ms tra un probe e l'altro
#define PACKET_SIZE           9

Servo servo;

// ==================== STATO ====================
enum RadioType { RADIO_NONE, RADIO_LORA, RADIO_NRF24 };
RadioType activeRadio = RADIO_NONE;

unsigned long lastPacketTime      = 0;
unsigned long lastProbeMs         = 0;
unsigned long lastVelocityUpdate  = 0;
float lastSteerNorm = 0.0f;

// ── Stato motore ──
bool    rx_freno             = false;
bool    rx_retro             = false;
uint8_t rx_pressione_pedale  = 0;
uint8_t rx_marcia            = 1;
float   velocita_target      = 0;
float   velocita_attuale     = 0;
bool    freno_premuto        = false;

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
  radio.openReadingPipe(1, nrfAddress);
  radio.startListening();
  return true;
}

RadioType detectRadio() {
  if (initLoRa())  return RADIO_LORA;
  if (initNRF24()) return RADIO_NRF24;
  return RADIO_NONE;
}

const char *radioName() {
  switch (activeRadio) {
    case RADIO_LORA:  return "LORA";
    case RADIO_NRF24: return "NRF24";
    default:          return "NONE";
  }
}

// ========== PROBE PERIODICO ==========
void probeRadio() {
  RadioType prev = activeRadio;

  bool stillAlive = false;
  if (prev == RADIO_LORA)  stillAlive = initLoRa();
  else if (prev == RADIO_NRF24) stillAlive = initNRF24();

  if (stillAlive) {
    activeRadio = prev;
    return;
  }

  RadioType found = detectRadio();
  activeRadio = found;

  if (found != prev) {
    Serial.print("RX MODULE_CHANGED ");
    Serial.println(radioName());
  }
}

// ========== ELABORAZIONE PACCHETTO ==========
void processPacket(const uint8_t *buf, int rssi) {
  if (buf[0] != 'V' || buf[1] != 'A' || buf[2] != 'L' || buf[3] != '1') {
    Serial.println("TOKEN_ERR");
    return;
  }

  uint16_t rxCrc   = ((uint16_t)buf[7] << 8) | buf[8];
  uint16_t calcCrc = crc16_ccitt(buf, 7);
  if (rxCrc != calcCrc) {
    Serial.println("CRC_ERR");
    return;
  }

  lastPacketTime = millis();

  uint8_t steerByte = buf[4];
  uint8_t accelByte = buf[5];
  uint8_t miscByte  = buf[6];

  uint8_t speedSel  = (miscByte >> 4) & 0x0F;
  bool    brake     = (miscByte >> 3) & 0x01;
  bool    reverse   = (miscByte >> 2) & 0x01;
  uint8_t commands  = miscByte & 0x03;

  // ── Sterzo → servo ──
  float steerNorm = ((float)steerByte - 128.0f) / 127.0f;
  steerNorm = constrain(steerNorm, -1.0f, 1.0f);
  if (fabs(steerNorm) < DEADZONE) steerNorm = 0.0f;

  if (fabs(steerNorm - lastSteerNorm) >= 0.02f) {
    lastSteerNorm = steerNorm;
    int angle = SERVO_CENTER + (int)(steerNorm * STEER_ANGLE_MAX);
    angle = constrain(angle,
                      SERVO_CENTER - STEER_ANGLE_MAX,
                      SERVO_CENTER + STEER_ANGLE_MAX);
    servo.write(angle);
  }

  // ── Aggiorna stato motore ──
  rx_freno            = brake;
  rx_retro            = reverse;
  rx_pressione_pedale = accelByte;
  rx_marcia           = map(speedSel, 0, 15, 1, MAX_SPEEDS);

  // ── Output seriale ──
  Serial.print("S:");   Serial.print(steerNorm, 2);
  Serial.print(" A:");  Serial.print((float)accelByte / 255.0f, 2);
  Serial.print(" B:");  Serial.print(brake ? "Y" : "N");
  Serial.print(" G:");  Serial.print(rx_marcia);
  Serial.print(" R:");  Serial.print(reverse ? "Y" : "N");
  Serial.print(" C:");  Serial.print(commands);
  if (activeRadio == RADIO_LORA) {
    Serial.print(" RSSI:"); Serial.print(rssi);
  }
  Serial.println();
}

// ======================== SETUP ========================
void setup() {
  Serial.begin(115200);
  delay(1000);
  SPI.begin();

  servo.attach(SERVO_PIN, 500, 2400);
  servo.write(SERVO_CENTER);

  // Motore
  ledcAttach(PWM_PIN, PWM_FREQ, PWM_RES);
  pinMode(DIR_FWD_PIN, OUTPUT);
  pinMode(DIR_REV_PIN, OUTPUT);
  digitalWrite(DIR_FWD_PIN, LOW);
  digitalWrite(DIR_REV_PIN, LOW);

  activeRadio = detectRadio();

  if (activeRadio == RADIO_NONE) {
    Serial.println("ERR NO_RADIO");
    // Non blocchiamo: il probe periodico ritenterà
  } else {
    Serial.print("RX READY ");
    Serial.println(radioName());
  }
}

// ======================== LOOP =========================
void loop() {
  // ── Probe periodico ──
  unsigned long now = millis();
  if (now - lastProbeMs >= PROBE_INTERVAL_MS) {
    lastProbeMs = now;
    probeRadio();
  }

  // ── Failsafe ──
  if (lastPacketTime > 0 && (millis() - lastPacketTime > FAILSAFE_MS)) {
    servo.write(SERVO_CENTER);
    ledcWrite(PWM_PIN, 0);
    digitalWrite(DIR_FWD_PIN, LOW);
    digitalWrite(DIR_REV_PIN, LOW);
    velocita_attuale = 0;
    velocita_target  = 0;
    lastPacketTime = 0;
    Serial.println("FAILSAFE");
  }

  // ── Ricezione pacchetto ──
  uint8_t buf[PACKET_SIZE] = {0};

  if (activeRadio == RADIO_LORA) {
    int pktSize = LoRa.parsePacket(PACKET_SIZE);
    if (pktSize == PACKET_SIZE) {
      for (int i = 0; i < PACKET_SIZE; i++) buf[i] = LoRa.read();
      processPacket(buf, LoRa.packetRssi());
    }
  }
  else if (activeRadio == RADIO_NRF24) {
    if (radio.available()) {
      radio.read(buf, PACKET_SIZE);
      processPacket(buf, 0);
    }
  }

  // ── Aggiornamento velocità e motore (ogni 10 ms) ──
  if (millis() - lastVelocityUpdate >= 40) {
    lastVelocityUpdate = millis();

    // 1. Calcolo velocità target
    if (rx_freno) {
      velocita_target = 0;
      freno_premuto = true;
    }
    else if (rx_retro) {
      velocita_target = -((float)(rx_pressione_pedale * rx_marcia) / MAX_SPEEDS) / 2.0f;
      freno_premuto = false;
    }
    else {
      velocita_target = (float)(rx_pressione_pedale * rx_marcia) / MAX_SPEEDS;
      freno_premuto = false;
    }

    // 2. Aggiornamento velocità attuale
    if (freno_premuto) {
      if (velocita_attuale > 0)      velocita_attuale -= 2;
      else if (velocita_attuale < 0) velocita_attuale += 2;
      if (fabs(velocita_attuale) < 2) velocita_attuale = 0;
    }
    else {
      if (velocita_attuale < velocita_target)      velocita_attuale++;
      else if (velocita_attuale > velocita_target) velocita_attuale--;
    }

    // 3. Output motore
    int pwmVal = constrain(abs((int)velocita_attuale), 0, 255);
    ledcWrite(PWM_PIN, pwmVal);

    if (velocita_attuale > 0) {
      digitalWrite(DIR_FWD_PIN, HIGH);
      digitalWrite(DIR_REV_PIN, LOW);
    }
    else if (velocita_attuale < 0) {
      digitalWrite(DIR_FWD_PIN, LOW);
      digitalWrite(DIR_REV_PIN, HIGH);
    }
    else {
      digitalWrite(DIR_FWD_PIN, LOW);
      digitalWrite(DIR_REV_PIN, LOW);
    }
  }
}