import cv2
import numpy as np
import os
import threading
import bluetooth
import time
import DetectChars
import DetectPlates
import PossiblePlate
from picamera.array import PiRGBArray
from picamera import PiCamera
import pymongo
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import pyautogui


shared_data = {
    'plate': None,
    'bluetooth_devices': set(),
    'rfid': None
}
data_lock = threading.Lock()
ultrasonic_triggered = False
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))


GPIO.setmode(GPIO.BCM)

# Module level variables
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)

showSteps = False
last_capture_time = 0

def ultrasonic_sensor():
    global ultrasonic_triggered
    Trig = 23
    Echo = 24

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Trig, GPIO.OUT)
    GPIO.setup(Echo, GPIO.IN)

    GPIO.output(Trig, False)

    # Add a delay of 5 seconds before starting
    time.sleep(5)

    while True:
        GPIO.output(Trig, True)
        time.sleep(0.00001)
        GPIO.output(Trig, False)

        while GPIO.input(Echo) == 0:
            debutImpulsion = time.time()

        while GPIO.input(Echo) == 1:
            finImpulsion = time.time()

        distance = round((finImpulsion - debutImpulsion) * 340 * 100 / 2, 1)

        print("Distance:", distance, "cm")

        if distance < 50:
            # Set the flag to indicate ultrasonic detection
            ultrasonic_triggered = True
        else:
            # Reset the flag when no object is detected within 50cm
            ultrasonic_triggered = False

        if ultrasonic_triggered:
            # Trigger the capture process when an object is detected within 50cm
            capture_image = True
            ultrasonic_triggered = False  # Reset the flag to avoid multiple captures

        time.sleep(1)  # Adjust the delay as needed
def get_ultrasonic_distance():
    Trig = 23
    Echo = 24

    GPIO.setup(Trig, GPIO.OUT)
    GPIO.setup(Echo, GPIO.IN)

    GPIO.output(Trig, False)

    time.sleep(0.5)  # Short delay for stability

    GPIO.output(Trig, True)
    time.sleep(0.00001)
    GPIO.output(Trig, False)

    while GPIO.input(Echo) == 0:
        start_time = time.time()

    while GPIO.input(Echo) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = round(elapsed_time * 34300 / 2, 2)  # Calculate distance in cm

    return distance

def read_rfid():
    global shared_data
    reader = SimpleMFRC522()

    try:
        while True:
            id, text = reader.read()
            with data_lock:
                shared_data['rfid'] = id  # Store only the ID
            print(f"RFID Read: ID - {id}")
            time.sleep(1)  # Add a delay to prevent constant reading, adjust as needed

    finally:
        GPIO.cleanup()

def main():
    global shared_data, data_lock

    blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()  # Attempt KNN training

    if not blnKNNTrainingSuccessful:  # If KNN training was not successful
        print("\nerror: KNN training was not successful\n")  # Show error message
        return  # Exit program

    while True:
        capture_image = False
        show_distance = False
        distance_timer = time.time()

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            imgOriginalScene = frame.array.copy()  # Create a writable copy of the image

            if capture_image:
                cv2.destroyWindow("imgOriginalScene")  # Destroy the previous image processing window
                cv2.destroyWindow("imgPlate")
                cv2.destroyWindow("imgThresh")

            cv2.imshow("Frame", imgOriginalScene)
            key = cv2.waitKey(1) & 0xFF
            rawCapture.truncate(0)

            if key == ord("s"):
                capture_image = True

            if time.time() - distance_timer > 5:  # Check distance every 5 seconds
                show_distance = True
                distance_timer = time.time()

            if show_distance:
                distance = get_ultrasonic_distance()  # Get the ultrasonic distance
                if distance < 50:
                    pyautogui.press('s')  # Simulate pressing the "s" key
                print("Distance:", distance, "cm")
                show_distance = False

            if capture_image:  # This block will execute if capture_image is True
                if imgOriginalScene is None:
                    print("\nerror: image not read from file \n\n")
                    os.system("pause")
                    return
                listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)  # Detect plates
                listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)  # Detect chars in plates

                cv2.imshow("imgOriginalScene", imgOriginalScene)  # Show scene image

                if not listOfPossiblePlates:  # If no plates were found
                    print("\nno license plates were detected\n")  # Inform user no plates were found
                else:
                    listOfPossiblePlates.sort(key=lambda possiblePlate: len(possiblePlate.strChars), reverse=True)
                    licPlate = listOfPossiblePlates[0]  # The actual plate is the one with the most recognized chars
                    cv2.imshow("imgPlate", licPlate.imgPlate)  # Show crop of plate and threshold of plate
                    cv2.imshow("imgThresh", licPlate.imgThresh)

                    if licPlate.strChars:  # If chars were found in the plate
                        with data_lock:
                            shared_data['plate'] = licPlate.strChars  # Update shared data with recognized license plate

                        drawRedRectangleAroundPlate(imgOriginalScene, licPlate)  # Draw red rectangle around plate

                        print("\nlicense plate read from image = " + licPlate.strChars + "\n")  # Write license plate text to std out
                        print("----------------------------------------")

                        writeLicensePlateCharsOnImage(imgOriginalScene, licPlate)  # Write license plate text on the image

                        cv2.imshow("imgOriginalScene", imgOriginalScene)  # Re-show scene image

                        cv2.imwrite("imgOriginalScene.png", imgOriginalScene)  # Write image out to file

                        cv2.destroyAllWindows()  # Close all OpenCV windows

                capture_image = False  # Reset capture_image to False after processing

            if key == ord("q"):
                return  # Return to exit the program
def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):
    if licPlate.rrLocationOfPlateInScene is None:
        print("No valid location for license plate.")
        return

    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)  # Get 4 vertices of rotated rect
    p2fRectPoints = [tuple(map(int, point)) for point in p2fRectPoints]

    # Draw lines
    cv2.line(imgOriginalScene, p2fRectPoints[0], p2fRectPoints[1], SCALAR_RED, 2)
    cv2.line(imgOriginalScene, p2fRectPoints[1], p2fRectPoints[2], SCALAR_RED, 2)
    cv2.line(imgOriginalScene, p2fRectPoints[2], p2fRectPoints[3], SCALAR_RED, 2)
    cv2.line(imgOriginalScene, p2fRectPoints[3], p2fRectPoints[0], SCALAR_RED, 2)

def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0  # This will be the center of the area the text will be written to
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0  # This will be the bottom left of the area that the text will be written to
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX  # Choose a plain jane font
    fltFontScale = float(plateHeight) / 30.0  # Base font scale on height of plate area
    intFontThickness = int(round(fltFontScale * 1.5))  # Base font thickness on font scale

    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)  # Call getTextSize

    # Unpack roatated rect into center point, width and height, and angle
    ((intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg) = licPlate.rrLocationOfPlateInScene

    intPlateCenterX = int(intPlateCenterX)  # Make sure center is an integer
    intPlateCenterY = int(intPlateCenterY)

    ptCenterOfTextAreaX = int(intPlateCenterX)  # The horizontal location of the text area is the same as the plate

    if intPlateCenterY < (sceneHeight * 0.75):  # If the license plate is in the upper 3/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))  # Write the chars in below the plate
    else:  # Else if the license plate is in the lower 1/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))  # Write the chars in above the plate

    textSizeWidth, textSizeHeight = textSize  # Unpack text size width and height

    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))  # Calculate the lower left origin of the text area
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))  # Based on the text area center, width, and height

    # Write the text on the image
    cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)

def delete_after_timeout(device_set, device, timeout):
    time.sleep(timeout)
    device_set.discard(device)
    print(f"Removed {device} from the set after {timeout} seconds")
    print("{Send list}", device_set)

def scan_devices():
    global shared_data, data_lock

    devs = set()

    while True:
        nearby_devices = bluetooth.discover_devices(duration=1, lookup_names=True, device_id=-1)

        for addr, name in nearby_devices:
            if addr not in devs:
                devs.add(addr)
                # Setting a timeout (e.g., 10 seconds) for each device in the set
                timeout_seconds = 10
                threading.Thread(target=delete_after_timeout, args=(devs, addr, timeout_seconds)).start()

            print("   {} - {}".format(addr, name))

        # Update shared data with the current set of Bluetooth devices
        with data_lock:
            shared_data['bluetooth_devices'] = devs.copy()

        # Time to wait before scanning again for Bluetooth devices
        time.sleep(0.2)  # Adjust the sleep duration as needed
        print("{Send list}", devs)

def bluetooth_scanning_thread():
    try:
        print("Bluetooth scanning started. Press Ctrl+C to stop.")
        scan_devices()
    except KeyboardInterrupt:
        print("\nBluetooth scanning stopped.")

def license_plate_recognition_thread():
    main()  # Assuming 'main' is your license plate recognition main function

def send_data_to_mongodb():
    # MongoDB setup
    mongo_host = '10.188.247.252'
    mongo_port = 27017
    database_name = 'smartparking'
    collection_name = 'datadump'

    client = pymongo.MongoClient(f'mongodb://{mongo_host}:{mongo_port}/')
    db = client[database_name]
    collection = db[collection_name]

    previous_plate = None  # Initialize with None to detect the first plate

    while True:
        with data_lock:
            current_plate = shared_data['plate']
            bluetooth_devices = list(shared_data['bluetooth_devices'])
            rfid = shared_data['rfid']  # Now 'rfid' is just the ID

        if current_plate and current_plate != previous_plate:
            data_to_insert = {
                'plate': current_plate,
                'bluetooth_devices': bluetooth_devices,
                'rfid': rfid
            }

            collection.insert_one(data_to_insert)
            print("Data has been sent to MongoDB.")

            # Update the previous_plate with the current_plate
            previous_plate = current_plate

        time.sleep(1)  # Adjust the frequency of updates as needed

    client.close()
# In your __main__ block
data_thread = threading.Thread(target=send_data_to_mongodb)
data_thread.start()

if __name__ == "__main__":
    # Create threads for each functionality
    data_thread = threading.Thread(target=send_data_to_mongodb)
    bt_thread = threading.Thread(target=bluetooth_scanning_thread)
    lpr_thread = threading.Thread(target=license_plate_recognition_thread)
    rfid_thread = threading.Thread(target=read_rfid)  # Create RFID thread

    # Start threads
    bt_thread.start()
    lpr_thread.start()
    rfid_thread.start()  # Start the RFID thread

    # Wait for threads to complete (if needed)
    bt_thread.join()
    lpr_thread.join()
    rfid_thread.join()  # Join RFID thread

    print("Program completed.")
