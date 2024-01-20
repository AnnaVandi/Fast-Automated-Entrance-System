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

shared_data = {
    'plate': None,
    'bluetooth_devices': set(),
    'rfid': None,
    'new_plate_detected': False 
}
data_lock = threading.Lock()



camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))

# module level variables ##########################################################################
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)

showSteps = False
last_capture_time = 0


def read_rfid():
    global shared_data
    reader = SimpleMFRC522()

    try:
        GPIO.setwarnings(False)  # Disable GPIO warnings
        while True:
            id, text = reader.read()
            with data_lock:
                shared_data['rfid'] = id  # Store only the ID
            print(f"RFID Read: ID - {id}")
            time.sleep(1)  # Add a delay to prevent constant reading, adjust as needed

    finally:
        GPIO.cleanup()
###################################################################################################
def main():
    global shared_data, data_lock

    blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()  # attempt KNN training

    if not blnKNNTrainingSuccessful:  # if KNN training was not successful
        print("\nerror: KNN training was not successful\n")  # show error message
        return  # and exit program

    previous_plate = None  # Variable to store the previous plate for comparison

    while True:
        capture_image = False
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            imgOriginalScene = frame.array.copy()  # create a writable copy of the image

            if capture_image:
                cv2.destroyWindow("imgOriginalScene")  # destroy the previous image processing window
                cv2.destroyWindow("imgPlate")
                cv2.destroyWindow("imgThresh")

            cv2.imshow("Frame", imgOriginalScene)
            key = cv2.waitKey(1) & 0xFF
            rawCapture.truncate(0)

            if key == ord("s"):
                capture_image = True

            if capture_image:  # this block will execute if capture_image is True
                if imgOriginalScene is None:
                    print("\nerror: image not read from file \n\n")
                    os.system("pause")
                    return
                listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)  # detect plates
                listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)  # detect chars in plates

                if not listOfPossiblePlates:  # if no plates were found
                    print("\nno license plates were detected\n")  # inform user no plates were found
                else:
                    listOfPossiblePlates.sort(key=lambda possiblePlate: len(possiblePlate.strChars), reverse=True)
                    licPlate = listOfPossiblePlates[0]  # the actual plate is the one with the most recognized chars

                    if licPlate.strChars and licPlate.strChars != previous_plate:  # Check if the plate is new
                        previous_plate = licPlate.strChars
                        with data_lock:
                            shared_data['plate'] = licPlate.strChars
                            shared_data['new_plate_detected'] = True  # Set flag for new plate detection

                        # Display and save the plate image
                        cv2.imshow("imgPlate", licPlate.imgPlate)  # show crop of plate
                        cv2.imshow("imgThresh", licPlate.imgThresh)  # show threshold of plate
                        print("\nlicense plate read from image = " + licPlate.strChars + "\n")  # write license plate text to std out
                        cv2.imwrite("imgOriginalScene.png", imgOriginalScene)  # write image out to file

                capture_image = False  # reset capture_image to False after processing

            if key == ord("q"):
                return  # return to exit the program
###################################################################################################
def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):
    if licPlate.rrLocationOfPlateInScene is None:
        print("No valid location for license plate.")
    return

    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)  # get 4 vertices of rotated rect

    p2fRectPoints = [tuple(map(int, point)) for point in p2fRectPoints]

    # Draw lines
    cv2.line(imgOriginalScene, p2fRectPoints[0], p2fRectPoints[1], SCALAR_RED, 2)
    cv2.line(imgOriginalScene, p2fRectPoints[1], p2fRectPoints[2], SCALAR_RED, 2)
    cv2.line(imgOriginalScene, p2fRectPoints[2], p2fRectPoints[3], SCALAR_RED, 2)
    cv2.line(imgOriginalScene, p2fRectPoints[3], p2fRectPoints[0], SCALAR_RED, 2)

###################################################################################################
def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0                             # this will be the center of the area the text will be written to
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0                          # this will be the bottom left of the area that the text will be written to
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX                      # choose a plain jane font
    fltFontScale = float(plateHeight) / 30.0                    # base font scale on height of plate area
    intFontThickness = int(round(fltFontScale * 1.5))           # base font thickness on font scale

    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)        # call getTextSize

            # unpack roatated rect into center point, width and height, and angle
    ( (intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg ) = licPlate.rrLocationOfPlateInScene

    intPlateCenterX = int(intPlateCenterX)              # make sure center is an integer
    intPlateCenterY = int(intPlateCenterY)

    ptCenterOfTextAreaX = int(intPlateCenterX)         # the horizontal location of the text area is the same as the plate

    if intPlateCenterY < (sceneHeight * 0.75):                                                  # if the license plate is in the upper 3/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))      # write the chars in below the plate
    else:                                                                                       # else if the license plate is in the lower 1/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))      # write the chars in above the plate
    # end if

    textSizeWidth, textSizeHeight = textSize                # unpack text size width and height

    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))           # calculate the lower left origin of the text area
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))          # based on the text area center, width, and height

            # write the text on the image
    cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)
# end function







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

    while True:
        with data_lock:
            if shared_data['new_plate_detected']:  # Check if a new plate was detected
                data_to_insert = {
                    'plate': shared_data['plate'],
                    'bluetooth_devices': list(shared_data['bluetooth_devices']),
                    'rfid': shared_data['rfid']
                }
                collection.insert_one(data_to_insert)
                print("Data has been sent to MongoDB.")
                shared_data['new_plate_detected'] = False  # Reset the flag

        time.sleep(1)  # Adjust the frequency of updates as needed
    client.close()
# In your __main__ block
data_thread = threading.Thread(target=send_data_to_mongodb)
data_thread.start()

def ultrasonic_sensor():
    Trig = 23
    Echo = 24

    GPIO.setup(Trig, GPIO.OUT)
    GPIO.setup(Echo, GPIO.IN)

    GPIO.output(Trig, False)

    while True:
        GPIO.output(Trig, True)
        time.sleep(0.00001)
        GPIO.output(Trig, False)

        while GPIO.input(Echo) == 0:
            debutImpulsion = time.time()

        while GPIO.input(Echo) == 1:
            finImpulsion = time.time()

        distance = round((finImpulsion - debutImpulsion) * 340 * 100 / 2, 1)

        print("Distance: ", distance, " cm")

        if distance < 50:
            # Trigger image capture as if the 's' key was pressed
            with data_lock:
                shared_data['capture_image'] = True


###################################################################################################
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
