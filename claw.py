import time
import configparser
from adafruit_servokit import ServoKit

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Servo settings
# CLAW_SERVO_CHANNEL = config.getint("CLAW", "channel", fallback=0)
# OPEN_PULSE = config.getint("CLAW", "open_pulse", fallback=2500)  # Calibrate (e.g., 500-2500)
# CLOSED_PULSE = config.getint("CLAW", "closed_pulse", fallback=500)  # Calibrate
# PULSE_STEP = config.getint("CLAW", "pulse_step", fallback=10)  # Step size for gradual slide

# # Initialize PCA9685 servo controller
# try:
#     i2c = busio.I2C(SCL, SDA)
#     pwm = PCA9685(i2c)
#     pwm.set_pwm_freq(50)  # 50Hz for servos
#     print("PCA9685 initialized for claw servo")
# except Exception as e:
#     print(f"Error initializing PCA9685: {e}")
#     pwm = None

# Initialize servo hat 
hat = ServoKit(channels = 16)
servo = hat.servo[4]
servo.actuation_range = config.getint("CLAW", "range", fallback=270)
MAX_ROTATION = config.getint("CLAW", "maxrotation", fallback=180)
STEP = config.getint("CLAW", "step", fallback=5) # how many degrees to turn per command
OPEN = 1
CLOSE = -1 
HOLD = 0

# Track current state and pulse
current_state = OPEN  # Start at closed position
# claw_state = 0  # 0: holding, 1: opening, -1: closing
current_angle = 0

# def set_servo_pulse(channel, pulse):
    # """Set PWM pulse for the claw servo, clamping to valid range."""
    # global current_pulse
    # if pwm is None:
    #     print("PCA9685 not initialized, cannot set servo pulse")
    #     return False, "PCA9685 not initialized"
    # try:
    #     # Clamp pulse to valid range
    #     pulse_us = max(CLOSED_PULSE, min(OPEN_PULSE, pulse_us))
    #     duty_cycle = int((pulse_us / 20000.0) * 65535)
    #     pwm.channels[channel].duty_cycle = duty_cycle
    #     pwm.set_pwm(channel, 0, pulse)
    #     current_pulse = pulse_us
    #     print(f"Claw servo channel {channel} set to pulse {pulse}")
    #     return True, f"Pulse set to {pulse}"
    # except Exception as e:
    #     print(f"Error setting claw servo PWM: {e}")
    #     return False, str(e)

def control_claw(command):
    if command == OPEN: 
        if current_angle < MAX_ROTATION: 
            current_angle = current_angle + STEP
    if command == CLOSE: 
        if current_angle > 0:
            current_angle = current_angle - STEP
    servo.angle = current_angle
    # """Process claw command (1: open, -1: close, 0: hold/stop). Returns success and status message."""
    # global claw_state, current_pulse
    # if command == 1:  # Open (D-Pad Right)
    #     new_pulse = min(OPEN_PULSE, current_pulse + PULSE_STEP)
    #     success, message = set_servo_pulse(CLAW_SERVO_CHANNEL, new_pulse)
    #     claw_state = 1 if new_pulse < OPEN_PULSE else 0  # Stop state if fully open
    #     return success, "Claw opening" if new_pulse < OPEN_PULSE else "Claw fully open"
    # elif command == -1:  # Close (D-Pad Left)
    #     new_pulse = max(CLOSED_PULSE, current_pulse - PULSE_STEP)
    #     success, message = set_servo_pulse(CLAW_SERVO_CHANNEL, new_pulse)
    #     claw_state = -1 if new_pulse > CLOSED_PULSE else 0  # Stop state if fully closed
    #     return success, "Claw closing" if new_pulse > CLOSED_PULSE else "Claw fully closed"
    # else:  # Hold/stop (neutral or stop command)
    #     success, message = set_servo_pulse(CLAW_SERVO_CHANNEL, current_pulse)
    #     claw_state = 0
    #     return success, "Claw holding position"

if __name__ == "__main__":
    # Hold closed position when run standalone
    control_claw(0)