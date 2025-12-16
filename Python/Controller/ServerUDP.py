import socket
import json
import RPi.GPIO as GPIO
import time

# --- Setup servo ---
def angle_to_percent(angle):
    start = 4
    end = 12.5
    ratio = (end - start) / 180
    return start + angle * ratio

def rx_to_angle(rx_value):
    """Mappa RX da -1..1 a 0..180 gradi"""
    return int((rx_value + 1) * 90)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Setup servo
pwm_gpio = 12
frequence = 50
GPIO.setup(pwm_gpio, GPIO.OUT)
pwm = GPIO.PWM(pwm_gpio, frequence)
pwm.start(0)

# --- Setup server UDP ---
UDP_IP = "0.0.0.0"
UDP_PORT = 8080
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Server in ascolto...")

try:
    while True:
        data, addr = sock.recvfrom(4096)
        values = json.loads(data.decode())
        print("Ricevuto:", values)

        # Servo
        rx = values.get("RX", 0.0)
        angle = rx_to_angle(rx)
        duty = angle_to_percent(angle)
        pwm.ChangeDutyCycle(duty)

        # Stop se X
        if values.get("X", False):
            print("X premuto: chiusura server")
            break

except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
    sock.close()