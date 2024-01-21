
# Fast-Automated-Entrance-System README

## Introduction
Fast-Automated-Entrance-System is designed to automate parking lot entrances using advanced technologies for speed and security.

## Project Structure
```
Fast-Automated-Entrance-System
│   README.md
│
├───client_side (Python scripts, OCR, OpenCV)
├───mongodb (Database schema and files)
└───server_side (Node.js server, web assets)
```

## Setup and Installation

## Installation Commands

### Python Installation
- For Windows:
  ```
  Download and install from https://www.python.org/downloads/windows/
  ```
- For Linux:
  ```
  sudo apt-get update
  sudo apt-get install python3
  ```

### Node.js Installation
- For Windows:
  ```
  Download and install from https://nodejs.org/en/download/
  ```
- For Linux:
  ```
  sudo apt-get update
  sudo apt-get install nodejs
  sudo apt-get install npm
  ```

### MongoDB Installation
- For Windows:
  ```
  Download and install from https://www.mongodb.com/try/download/community
  ```
- For Linux:
  ```
  Follow the official guide at https://docs.mongodb.com/manual/administration/install-on-linux/
  ```

### Raspberry Pi Client-Side Scripts Setup
- Install Python (usually pre-installed on Raspberry Pi OS).
- Install OpenCV for Python:
  ```
  pip install opencv-python
  ```
- Install OCR libraries for Python (example for Tesseract OCR):
  ```
  sudo apt-get install tesseract-ocr
  pip install pytesseract
  ```

These commands will set up the necessary environment for running the Fast-Automated-Entrance-System on various platforms.


### Prerequisites
- Python, Node.js, MongoDB
- Raspberry Pi for client-side scripts
- OpenCV and OCR libraries for Python

### Database Setup
1. **MongoDB Import**:
   - Navigate to `mongodb/smartparking`.
   - Use `mongorestore` to import the database schema:
     ```
     mongorestore /path/to/smartparking
     ```

### Client-Side Setup (Raspberry Pi)
1. **Install Python, OpenCV, OCR**:
   - Run `pip install opencv-python`.
2. **Run Client Scripts**:
   - Transfer `client_side` to Raspberry Pi.
   - Run `python Mainx.py` (replace `x` with version number).

### Server-Side Setup
1. **Node.js Server**:
   - Navigate to `server_side`.
   - Install dependencies: `npm install`.
   - Start the server: `node server.js`.

### Accessing the Web Interface
- Open `http://localhost:3000` or server URL in a browser.


## Client-Side Setup (Raspberry Pi)
The client-side application is designed to run on a Raspberry Pi. It requires the installation of OpenCV for image processing and OCR (Optical Character Recognition) for license plate recognition.

### Prerequisites for Raspberry Pi
- Python installed.
- OpenCV installed for Python. You can install it using pip:
  ```
  pip install opencv-python
  ```
- OCR libraries installed for Python.

### Running the Client-Side Application
- Transfer the `client_side` directory to your Raspberry Pi.
- Navigate to the `client_side` directory on the Raspberry Pi.
- Run the latest `Mainx.py` script (where `x` is the version number). For example:
  ```
  python Main8.py
  ```
This script will initiate the processing and authentication mechanism essential for the Fast-Automated-Entrance-System to function. Ensure that all dependencies are correctly installed for the script to run successfully.



