/*
 * RxCompleto.ino — Ricezione Squadra Corse (robust link)
 */

#include <SPI.h>
#include <ESP32Servo.h>
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

#define SERVO_PIN       26
const int SERVO_CENTER = 90;

// MOTORE: PIN INVARIATI
#define PWM_PIN         25
#define DIR_FWD_PIN     33
#define DIR_REV_PIN     32
#define PWM_FREQ      1000
#define PWM_RES          8

#define STEER_ANGLE_MAX        45
#define DEADZONE            0.06f
#define PACKET_SIZE             7
#define PROBE_INTERVAL_MS    2000
#define LINK_TIMEOUT_MS       350
#define FAILSAFE_MS          1200
#define MOTOR_TICK_MS          20
#define STATS_INTERVAL_MS    5000
#define DEBUG_SERIAL        false

Servo servo;

enum RadioType { RADIO_NONE, RADIO_LORA, RADIO_NRF24 };
RadioType activeRadio = RADIO_NONE;

unsigned long lastPacketTime = 0;
unsigned long lastProbeMs = 0;
unsigned long lastVelocityUpdate = 0;
unsigned long lastStatsMs = 0;

float steer_target_norm = 0.0f;
float steer_current_norm = 0.0f;

bool    rx_freno = false;
bool    rx_retro = false;
uint8_t rx_pressione_pedale = 0;
float   velocita_target = 0;
float   velocita_attuale = 0;

bool hasSeq = false;
uint8_t lastSeq = 0;

uint32_t statPktOk = 0;
uint32_t statCrcErr = 0;
uint32_t statTokenErr = 0;
uint32_t statDup = 0;
uint32_t statLost = 0;

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
  radio.openReadingPipe(1, nrfAddress);
  radio.startListening();
  return true;
}

RadioType detectRadio() {
  if (initLoRa()) return RADIO_LORA;
  if (initNRF24()) return RADIO_NRF24;
  return RADIO_NONE;
}

const char *radioName() {
  switch (activeRadio) {
    case RADIO_LORA: return "LORA";
    case RADIO_NRF24: return "NRF24";
    default: return "NONE";
  }
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
    Serial.print("RX MODULE_CHANGED ");
    Serial.println(radioName());
  }
}

void updateSteering() {
  // Sterzo costante: mantiene target finché non arriva un nuovo comando.
  const float steer_step = 0.04f;
  if (steer_current_norm < steer_target_norm) steer_current_norm = min(steer_target_norm, steer_current_norm + steer_step);
  else if (steer_current_norm > steer_target_norm) steer_current_norm = max(steer_target_norm, steer_current_norm - steer_step);

  int angle = SERVO_CENTER + (int)(steer_current_norm * STEER_ANGLE_MAX);
  angle = constrain(angle, SERVO_CENTER - STEER_ANGLE_MAX, SERVO_CENTER + STEER_ANGLE_MAX);
  servo.write(angle);
}

void processPacket(const uint8_t *buf, int rssi) {
  if (buf[0] != 0xA2) {
    statTokenErr++;
    return;
  }

  uint16_t rxCrc = ((uint16_t)buf[5] << 8) | buf[6];
  uint16_t calcCrc = crc16_ccitt(buf, 5);
  if (rxCrc != calcCrc) {
    statCrcErr++;
    return;
  }

  uint8_t seq = buf[4];
  if (hasSeq) {
    uint8_t delta = (uint8_t)(seq - lastSeq);
    if (delta == 0) {
      statDup++;
      lastPacketTime = millis();
      return;
    }
    if (delta > 1) statLost += (uint32_t)(delta - 1);
  }
  hasSeq = true;
  lastSeq = seq;

  lastPacketTime = millis();
  statPktOk++;

  uint8_t steerByte = buf[1];
  uint8_t accelByte = buf[2];
  uint8_t miscByte = buf[3];

  float steerNorm = ((float)steerByte - 128.0f) / 127.0f;
  steerNorm = constrain(steerNorm, -1.0f, 1.0f);
  if (fabs(steerNorm) < DEADZONE) steerNorm = 0.0f;
  steer_target_norm = steerNorm;

  rx_freno = ((miscByte >> 3) & 0x01);
  rx_retro = ((miscByte >> 2) & 0x01);
  rx_pressione_pedale = accelByte;

  if (DEBUG_SERIAL && activeRadio == RADIO_LORA) {
    Serial.print("RSSI:");
    Serial.print(rssi);
    Serial.print(" ");
  }
}

void hardStop() {
  velocita_attuale = 0;
  velocita_target = 0;
  steer_target_norm = 0;
  steer_current_norm = 0;
  ledcWrite(PWM_PIN, 0);
  digitalWrite(DIR_FWD_PIN, LOW);
  digitalWrite(DIR_REV_PIN, LOW);
  servo.write(SERVO_CENTER);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  SPI.begin();

  servo.attach(SERVO_PIN, 500, 2400);
  servo.write(SERVO_CENTER);

  ledcAttach(PWM_PIN, PWM_FREQ, PWM_RES);
  pinMode(DIR_FWD_PIN, OUTPUT);
  pinMode(DIR_REV_PIN, OUTPUT);
  digitalWrite(DIR_FWD_PIN, LOW);
  digitalWrite(DIR_REV_PIN, LOW);

  activeRadio = detectRadio();

  if (activeRadio == RADIO_NONE) Serial.println("ERR NO_RADIO");
  else {
    Serial.print("RX READY ");
    Serial.println(radioName());
  }
}

void loop() {
  unsigned long now = millis();

  if (now - lastProbeMs >= PROBE_INTERVAL_MS) {
    lastProbeMs = now;
    probeRadio();
  }

  uint8_t buf[PACKET_SIZE] = {0};
  if (activeRadio == RADIO_LORA) {
    int pktSize = LoRa.parsePacket();
    if (pktSize == PACKET_SIZE) {
      for (int i = 0; i < PACKET_SIZE; i++) buf[i] = LoRa.read();
      processPacket(buf, LoRa.packetRssi());
    }
  } else if (activeRadio == RADIO_NRF24) {
    while (radio.available()) {
      radio.read(buf, PACKET_SIZE);
      processPacket(buf, 0);
    }
  }

  if (now - lastVelocityUpdate >= MOTOR_TICK_MS) {
    lastVelocityUpdate = now;

    unsigned long silence = (lastPacketTime == 0) ? FAILSAFE_MS + 1 : (now - lastPacketTime);

    if (silence > FAILSAFE_MS) {
      hardStop();
      return;
    }

    if (silence > LINK_TIMEOUT_MS) {
      rx_freno = true;
      rx_pressione_pedale = 0;
      // NON forzare steer_target_norm a zero: evita il ritorno a 0 improvviso in curva.
    }

    if (rx_freno) velocita_target = 0;
    else if (rx_retro) velocita_target = -((float)rx_pressione_pedale) * 0.5f;
    else velocita_target = (float)rx_pressione_pedale;

    if (velocita_attuale < velocita_target) velocita_attuale += 1.2f;
    else if (velocita_attuale > velocita_target) velocita_attuale -= (rx_freno ? 2.0f : 1.2f);
    if (fabs(velocita_attuale) < 1.0f) velocita_attuale = 0;

    int pwmVal = constrain(abs((int)velocita_attuale), 0, 255);
    ledcWrite(PWM_PIN, pwmVal);

    if (velocita_attuale > 0) {
      digitalWrite(DIR_FWD_PIN, HIGH);
      digitalWrite(DIR_REV_PIN, LOW);
    } else if (velocita_attuale < 0) {
      digitalWrite(DIR_FWD_PIN, LOW);
      digitalWrite(DIR_REV_PIN, HIGH);
    } else {
      digitalWrite(DIR_FWD_PIN, LOW);
      digitalWrite(DIR_REV_PIN, LOW);
    }

    updateSteering();
  }

  if (DEBUG_SERIAL && now - lastStatsMs >= STATS_INTERVAL_MS) {
    lastStatsMs = now;
    Serial.print("RX_STATS ok=");
    Serial.print(statPktOk);
    Serial.print(" lost=");
    Serial.print(statLost);
    Serial.print(" dup=");
    Serial.print(statDup);
    Serial.print(" crc=");
    Serial.print(statCrcErr);
    Serial.print(" token=");
    Serial.println(statTokenErr);
  }
}
