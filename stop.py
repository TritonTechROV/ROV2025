#!/usr/bin/env python3

import serial
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)

port = '/dev/ttyAMA0'
ser1 = serial.Serial(port, baudrate=9600, timeout=0.1)

GPIO.output(4, GPIO.HIGH)
GPIO.output(17, GPIO.HIGH)
ser1.write(bytes([0]))