/*
 * Rx.ino — Ricezione Squadra Corse – Macchina 2
 *
 * Pacchetto radio 9 byte:
 *   [0-3] Token "VAL2"
 *   [4]   Sterzo        (0-255, 128 = centro)
 *   [5]   Accelerazione (0-255)
 *   [6]   speed_sel:4 | brake:1 | reverse:1 | comandi:2
 *         speed_sel 0-9 → velocità max 10%-100% (step 10%)
 *   [7-8] CRC-16 CCITT  (big-endian, su byte 0-6)
 *
 * Controllo motore con rampa differenziata:
 *   - Accelerazione progressiva verso il target
 *   - Frenata rapida quando il freno è premuto
 *   - Decelerazione dolce in rilascio acceleratore (coast)
 *
 * PID sul servo sterzo per movimenti fluidi e stabili.
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
#define STEER_ANGLE_MAX     70
#define REVERSE_MULTIPLIER   0.5f
#define DEADZONE             0.08f
#define FAILSAFE_MS          500
#define PROBE_INTERVAL_MS   2000        // ms tra un probe e l'altro
#define PACKET_SIZE           9
#define UPDATE_INTERVAL_MS    20        // aggiornamento motore/servo (50 Hz)
#define NRF_CHANNEL          83         // Canale NRF24 – Macchina 2

// ── Token identificativo macchina ──
#define TOKEN_0 'V'
#define TOKEN_1 'A'
#define TOKEN_2 'L'
#define TOKEN_3 '2'

// ── Velocità percentuale (10 livelli: 10%..100%) ──
#define SPEED_LEVELS         10

// ── Rampe motore (unità PWM per tick di UPDATE_INTERVAL_MS) ──
#define ACCEL_RATE          2.5f
#define DECEL_COAST         1.2f
#define DECEL_BRAKE         4.0f

// ── Rampa cambio marcia (% per tick) ──
#define SPEED_PCT_RATE      1.5f

// ── Soglia minima PWM per vincere l'attrito statico ──
#define MOTOR_MIN_PWM       25

// ── PID Servo ──
#define SERVO_KP           0.35f
#define SERVO_KI           0.008f
#define SERVO_KD           0.20f
#define SERVO_I_MAX       30.0f

Servo servo;

// ==================== STATO ====================
enum RadioType { RADIO_NONE, RADIO_LORA, RADIO_NRF24 };
RadioType activeRadio = RADIO_NONE;

unsigned long lastPacketTime      = 0;
unsigned long lastProbeMs         = 0;
unsigned long lastVelocityUpdate  = 0;

// ── Stato motore ──
bool    rx_freno             = false;
bool    rx_retro             = false;
uint8_t rx_pressione_pedale  = 0;
uint8_t rx_speed_pct         = 10;
float   speed_pct_smooth     = 10.0f;
float   velocita_target      = 0;
float   velocita_attuale     = 0;

// ── Coast-to-stop ──
unsigned long zeroReachedMs  = 0;
int8_t        lastDirection  = 0;
#define COAST_HOLD_MS        2000

// ── PID Servo stato ──
float servo_target_angle     = SERVO_CENTER;
float servo_current_angle    = SERVO_CENTER;
float servo_integral         = 0.0f;
float servo_prev_error       = 0.0f;

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
  radio.setChannel(NRF_CHANNEL);
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
  if (buf[0] != TOKEN_0 || buf[1] != TOKEN_1 || buf[2] != TOKEN_2 || buf[3] != TOKEN_3) {
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

  float steerNorm = ((float)steerByte - 128.0f) / 127.0f;
  steerNorm = constrain(steerNorm, -1.0f, 1.0f);
  if (fabs(steerNorm) < DEADZONE) steerNorm = 0.0f;
  servo_target_angle = SERVO_CENTER + steerNorm * STEER_ANGLE_MAX;

  rx_freno            = brake;
  rx_retro            = reverse;
  rx_pressione_pedale = accelByte;
  rx_speed_pct        = min((int)(speedSel + 1) * 10, 100);

  Serial.print("S:");   Serial.print(steerNorm, 2);
  Serial.print(" A:");  Serial.print((float)accelByte / 255.0f, 2);
  Serial.print(" B:");  Serial.print(brake ? "Y" : "N");
  Serial.print(" V:");  Serial.print(rx_speed_pct); Serial.print("%");
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

  ledcAttach(PWM_PIN, PWM_FREQ, PWM_RES);
  pinMode(DIR_FWD_PIN, OUTPUT);
  pinMode(DIR_REV_PIN, OUTPUT);
  digitalWrite(DIR_FWD_PIN, LOW);
  digitalWrite(DIR_REV_PIN, LOW);

  activeRadio = detectRadio();

  if (activeRadio == RADIO_NONE) {
    Serial.println("ERR NO_RADIO");
  } else {
    Serial.print("RX READY ");
    Serial.println(radioName());
  }
}

// ======================== LOOP =========================
void loop() {
  unsigned long now = millis();
  if (now - lastProbeMs >= PROBE_INTERVAL_MS) {
    lastProbeMs = now;
    probeRadio();
  }

  if (lastPacketTime > 0 && (millis() - lastPacketTime > FAILSAFE_MS)) {
    servo.write(SERVO_CENTER);
    servo_current_angle = SERVO_CENTER;
    servo_target_angle  = SERVO_CENTER;
    servo_integral      = 0;
    servo_prev_error    = 0;
    ledcWrite(PWM_PIN, 0);
    digitalWrite(DIR_FWD_PIN, LOW);
    digitalWrite(DIR_REV_PIN, LOW);
    velocita_attuale    = 0;
    velocita_target     = 0;
    speed_pct_smooth    = 10.0f;
    rx_freno            = false;
    rx_retro            = false;
    rx_pressione_pedale = 0;
    rx_speed_pct        = 10;
    lastPacketTime = 0;
    Serial.println("FAILSAFE");
  }

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

  if (millis() - lastVelocityUpdate >= UPDATE_INTERVAL_MS) {
    lastVelocityUpdate = millis();

    float servoErr  = servo_target_angle - servo_current_angle;
    servo_integral += servoErr;
    servo_integral  = constrain(servo_integral, -SERVO_I_MAX, SERVO_I_MAX);
    float servoDer  = servoErr - servo_prev_error;
    servo_prev_error = servoErr;

    float pidOut = SERVO_KP * servoErr
                 + SERVO_KI * servo_integral
                 + SERVO_KD * servoDer;
    servo_current_angle += pidOut;
    servo_current_angle  = constrain(servo_current_angle,
                                     (float)(SERVO_CENTER - STEER_ANGLE_MAX),
                                     (float)(SERVO_CENTER + STEER_ANGLE_MAX));
    servo.write((int)(servo_current_angle + 0.5f));

    float pctTarget = (float)rx_speed_pct;
    float pctDiff   = pctTarget - speed_pct_smooth;
    if (fabs(pctDiff) < SPEED_PCT_RATE) {
      speed_pct_smooth = pctTarget;
    } else {
      speed_pct_smooth += copysignf(SPEED_PCT_RATE, pctDiff);
    }

    float max_pwm = 255.0f * speed_pct_smooth / 100.0f;

    if (rx_freno) {
      velocita_target = 0;
    } else if (rx_retro) {
      if (velocita_attuale > 0.5f) {
        velocita_target = 0;
      } else {
        velocita_target = -(rx_pressione_pedale / 255.0f) * max_pwm * REVERSE_MULTIPLIER;
      }
    } else {
      if (velocita_attuale < -0.5f) {
        velocita_target = 0;
      } else {
        velocita_target = (rx_pressione_pedale / 255.0f) * max_pwm;
      }
    }

    if (rx_freno) {
      if (fabs(velocita_attuale) <= DECEL_BRAKE) {
        velocita_attuale = 0;
      } else {
        velocita_attuale -= copysignf(DECEL_BRAKE, velocita_attuale);
      }
    } else {
      float diff = velocita_target - velocita_attuale;
      if (fabs(diff) < 0.5f) {
        velocita_attuale = velocita_target;
      } else {
        bool accelerating = (fabs(velocita_target) >= fabs(velocita_attuale));
        float rate;
        if (accelerating) {
          float progress = fabs(velocita_attuale) / fmaxf(fabs(velocita_target), 1.0f);
          rate = ACCEL_RATE * (0.4f + 0.6f * progress);
          rate = fmaxf(rate, ACCEL_RATE * 0.4f);
        } else {
          float absVel = fabs(velocita_attuale);
          if (absVel < 30.0f) {
            float ease = absVel / 30.0f;
            rate = DECEL_COAST * (0.3f + 0.7f * ease);
            rate = fmaxf(rate, 0.15f);
          } else {
            rate = DECEL_COAST;
          }
        }
        float step = fminf(fabs(diff), rate);
        velocita_attuale += copysignf(step, diff);
      }
      if (!rx_retro && velocita_attuale < 0) velocita_attuale = 0;
      if (rx_retro  && velocita_attuale > 0) velocita_attuale = 0;
    }

    int pwmVal = (int)(fabs(velocita_attuale) + 0.5f);
    if (pwmVal > 0 && pwmVal < MOTOR_MIN_PWM) pwmVal = MOTOR_MIN_PWM;
    pwmVal = constrain(pwmVal, 0, 255);
    ledcWrite(PWM_PIN, pwmVal);

    if (velocita_attuale > 0.5f) {
      digitalWrite(DIR_FWD_PIN, HIGH);
      digitalWrite(DIR_REV_PIN, LOW);
      lastDirection = 1;
      zeroReachedMs = 0;
    }
    else if (velocita_attuale < -0.5f) {
      digitalWrite(DIR_FWD_PIN, LOW);
      digitalWrite(DIR_REV_PIN, HIGH);
      lastDirection = -1;
      zeroReachedMs = 0;
    }
    else {
      if (zeroReachedMs == 0) zeroReachedMs = millis();

      if (millis() - zeroReachedMs < COAST_HOLD_MS && lastDirection != 0) {
        if (lastDirection > 0) {
          digitalWrite(DIR_FWD_PIN, HIGH);
          digitalWrite(DIR_REV_PIN, LOW);
        } else {
          digitalWrite(DIR_FWD_PIN, LOW);
          digitalWrite(DIR_REV_PIN, HIGH);
        }
      } else {
        digitalWrite(DIR_FWD_PIN, LOW);
        digitalWrite(DIR_REV_PIN, LOW);
        lastDirection = 0;
      }
    }
  }
}
