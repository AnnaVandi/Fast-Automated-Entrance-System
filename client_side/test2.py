import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# PIR sensor setup
PIR_PIN = 21
GPIO.setup(PIR_PIN, GPIO.IN)

def motion_detected(PIR_PIN):
    print("Motion Detected!")

print("Starting PIR Motion Sensor...")
time.sleep(2)  # Allow sensor to warm up
print("PIR Motion Sensor Ready")

try:
    GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=motion_detected)

    # Keep the script running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting PIR Motion Sensor")
    GPIO.cleanup()  # Clean up GPIO on CTRL+C exit
