# ROV2025
Triton Tech ROV's 2025 ROV Design &amp; Code

The ROV this code was written for is headed to the MATE ROV 2025 competition in Alpena, Michigan to compete at the Pioneer level. This code has been written by members of Edmonds College Triton Tech ROV team. We provide no guarantee that it will work when you install it, and we're still tweaking and troubleshooting it. 

Things we haven't done yet: 
- Made the server reliable (we often have to reboot it to get it to reliably connect, but we're working on it!)
- Gotten all the cameras to work (which is why it currently only sets up the "front" camera)
- Finished the code for the claw (or the claw itself) 
- Made the webpage pretty 

## How to Use
### Electronics:
On board the ROV we designed is a Raspberry Pi connected to an [Adafruit Servo Hat](https://www.adafruit.com/product/2327) for our claw servos. Two [Sabertooth 2x5 motor controllers](https://www.dimensionengineering.com/products/sabertooth2x5) are connected to it. Wire the two motor controllers' S2 inputs to pins 4 and 17 (one pin for each controller) on the Pi. Wire the serial output pin on the pi to S1 on both Sabertooths. Make sure that the switches on the sabertooth are all turned "ON" except for 2, 4, and 6. Then, connect your thrusters to the Sabertooths. Follow the Sabertooth manual to finish connecting power, signal power/ground, and thrusters. Ensure that you have dedicated power for the sabertooths! We connected the "battery" terminals on the sabertooth to two of the servo 5V/Ground sets on the servo hat and it's working great. *CAREFUL: THE NON-SERVO 5V PINS ON THE SERVO HAT PULL POWER FROM THE PI, NOT DEDICATED MOTOR POWER!* Our configuration, which the code reflects, is: 
- Sabertooth 1 - connected to pin 4 - up/down thrusters 
- Sabertooth 2 - connected to pin 17 - forward/back thrusters (port thruster has output 1, starboard thruster has output 2) 
In the future, we may add a circuit diagram to this README for additional reference. 
### Code: 
SSH into the onboard Pi or otherwise open a terminal on it. Clone this repository to a convenient folder on the Pi. Copy `config_template.ini` to `config.ini` and edit it as explained below. To start the server, run `backend.py`. The terminal will give you a link to the associated webpage. 
#### Config: 
If you are using a Raspberry Pi 4B configured to use the hardware serial, you may not need to change any settings except for adding paths to the cameras. Look into your cameras' drivers to see how to find their addresses and place those in the appropriate section of the config. You may also want to change the username and password for the webpage. 