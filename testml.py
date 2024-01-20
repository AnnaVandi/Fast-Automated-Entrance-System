import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
SIGNAL_PIN = 17
GPIO.setup(SIGNAL_PIN, GPIO.IN)

try:
    while True:
        signal = GPIO.input(SIGNAL_PIN)
        print("Signal: ", signal)
        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
