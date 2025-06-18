import time
import configparser
from adafruit_servokit import ServoKit
import threading

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Initialize servo
kit = ServoKit(channels=16)
servo = kit.servo[4]
servo.actuation_range = config.getint("CLAW", "range", fallback=270)
MAX_ROTATION = config.getint("CLAW", "maxrotation", fallback=180)
STEP = config.getint("CLAW", "step", fallback=5)
DELAY = 0.05  # movement delay

# Claw directions
OPEN = 1
CLOSE = -1
HOLD = 0

# Global state
current_angle = 0
command = HOLD

def set_command(new_cmd):
    global command
    command = new_cmd

def control_claw():
    global current_angle, command
    while True:
        if command == OPEN and current_angle < MAX_ROTATION:
            current_angle += STEP
            current_angle = min(current_angle, MAX_ROTATION)
            servo.angle = current_angle
        elif command == CLOSE and current_angle > 0:
            current_angle -= STEP
            current_angle = max(current_angle, 0)
            servo.angle = current_angle
        time.sleep(DELAY)
