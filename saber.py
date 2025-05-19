#!/usr/bin/env python3

'''
    Seperate file for communication with the Sabertooths. Sabertooths should be in
    simplified serial mode, and the up and forward Sabertooth enable pins should be
    connected to pins 4 and 17 respectively, unless configured differently.
    
    If ran standalone, stops both sabertooths.
'''

import serial
import RPi.GPIO as GPIO
import configparser
import time

config = configparser.ConfigParser()
config.read("config.ini")

def intToBytes(integer):
    return bytes([integer])

# Constants
UPSABER = 4
FORWARDSABER = 17
ON = GPIO.HIGH
OFF = GPIO.LOW
FORWARD1 = intToBytes(127)
FORWARD2 = intToBytes(255)
BACK1 = intToBytes(1)
BACK2 = intToBytes(128)
ALLSTOP = intToBytes(0)
STOP1 = intToBytes(64)
STOP2 = intToBytes(192)
SLEEP_TIME = 0.001
serialPath = config.get("CONTROL", "serial", fallback="/dev/ttyAMA0")

# Sabertooth setup
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)  # Suppress GPIO warnings
    GPIO.setup(UPSABER, GPIO.OUT)
    GPIO.setup(FORWARDSABER, GPIO.OUT)
    try:
        ser1 = serial.Serial(serialPath, baudrate=9600, timeout=0.1)
        print("Sabertooths set up.")
    except serial.SerialException as e:
        print(f"Failed to open {serialPath}: {e}")
        exit(1)
    return ser1

ser1 = setup()

def activate(whichSaber):
    time.sleep(SLEEP_TIME)
    GPIO.output(whichSaber, ON)

def deactivate(whichSaber):
    time.sleep(SLEEP_TIME)
    GPIO.output(whichSaber, OFF)

def deactivateAll():
    deactivate(UPSABER)
    deactivate(FORWARDSABER)

def forward():
    activate(FORWARDSABER)
    deactivate(UPSABER)
    ser1.write(FORWARD1)
    time.sleep(SLEEP_TIME)
    ser1.write(FORWARD2)
    deactivate(FORWARDSABER)

def backward():
    activate(FORWARDSABER)
    deactivate(UPSABER)
    ser1.write(BACK1)
    time.sleep(SLEEP_TIME)
    ser1.write(BACK2)
    deactivate(FORWARDSABER)

def right():
    activate(FORWARDSABER)
    deactivate(UPSABER)
    ser1.write(FORWARD2)
    time.sleep(SLEEP_TIME)
    ser1.write(STOP1)
    deactivate(FORWARDSABER)

def hardRight():
    activate(FORWARDSABER)
    deactivate(UPSABER)
    ser1.write(FORWARD2)
    time.sleep(SLEEP_TIME)
    ser1.write(BACK1)
    deactivate(FORWARDSABER)

def left():
    activate(FORWARDSABER)
    deactivate(UPSABER)
    ser1.write(FORWARD1)
    time.sleep(SLEEP_TIME)
    ser1.write(STOP2)
    deactivate(FORWARDSABER)

def hardLeft():
    activate(FORWARDSABER)
    deactivate(UPSABER)
    ser1.write(FORWARD1)
    time.sleep(SLEEP_TIME)
    ser1.write(BACK2)
    deactivate(FORWARDSABER)

def up():
    activate(UPSABER)
    ser1.write(FORWARD1)
    time.sleep(SLEEP_TIME)
    ser1.write(FORWARD2)
    deactivate(UPSABER)

def stopforwardback():
    activate(FORWARDSABER)
    ser1.write(ALLSTOP)
    deactivate(FORWARDSABER)

def stopupdown():
    activate(UPSABER)
    ser1.write(ALLSTOP)
    deactivate(FORWARDSABER)

def down():
    activate(UPSABER)
    ser1.write(BACK1)
    time.sleep(SLEEP_TIME)
    ser1.write(BACK2)
    deactivate(UPSABER)

def stop():
    activate(FORWARDSABER)
    activate(UPSABER)
    ser1.write(ALLSTOP)
    deactivateAll()

if __name__ == '__main__':
    stop()
