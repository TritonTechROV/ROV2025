#!/usr/bin/env python3

'''
    File for the websocket handler.
'''

import time
import asyncio
import websockets
import json
import configparser
# Local imports
import saber
config = configparser.ConfigParser()
config.read("config.ini")

UPDATE_SPEED = config.getint("WEB", "tickspeed", fallback=60)
PORT = config.getint("WEB", "sockport", fallback=8765)
DEADZONE = config.getfloat("CONTROL", "deadzone", fallback=0.1)
HOST = config.get("WEB", "host", fallback="127.0.0.1")

last_command = None

'''
    What the big red "Stop" button should do
'''
def eStop():
    print("Stop command received")
    #ser1.write(ALLSTOP)
    saber.deactivateAll()
    saber.stop()

'''
        Parses data in message
        
        Runs estop procedure and returns None if the message is "stop". If not, returns gamepad status
'''
def parsePacket(message):
    gamepad = {"vertical": 0.0, "yaw": 0.0, "thrust": 0.0, "claw": 0}
    if message["type"] == "gamepad":
        gamepad.update({
            "vertical": float(message["vertical"]),
            "yaw": float(message["yaw"]),
            "thrust": float(message["thrust"]),
            "claw": float(message["claw"])
        })
    
    elif message["type"] == "stop":
        eStop()
        return None
    
    return gamepad

async def send_status(websocket, message):
        try:
            await websocket.send(json.dumps({"message": message}))
        except:
            pass

async def handleWebsocket(websocket):
    global last_command
    threshold = 0.5  # Threshold for hard turns
    gamepad_data = {"vertical": 0.0, "yaw": 0.0, "thrust": 0.0, "claw": 0}

    print("Sabertooth initialized")
   
    while True:
        try:
            async for message in websocket:
                data = json.loads(message)
                new_data = parsePacket(data)
                # Stop command received
                if new_data == None:
                    await send_status(websocket, "ROV stopped")
                    last_command = None
                    continue
                else:
                    gamepad_data = new_data
                 
                # Map gamepad data to Sabertooth commands
                current_command = None
                if abs(gamepad_data["vertical"]) > DEADZONE:
                    if gamepad_data["vertical"] > 0:
                        saber.up()
                        current_command = "up"
                    else:
                        saber.down()
                        current_command = "down"
                if abs(gamepad_data["thrust"]) > DEADZONE:
                    if gamepad_data["thrust"] > 0: 
                        saber.forward()
                        current_command="forward"
                    else:
                        saber.backward()
                        current_command="backward"
                if abs(gamepad_data["yaw"]) > DEADZONE:
                    if gamepad_data["yaw"] > threshold:
                        saber.hardRight()
                        current_command = "hardRight"
                    elif gamepad_data["yaw"] > 0:
                        saber.right()
                        current_command = "right"
                    elif gamepad_data["yaw"] < -threshold:
                        saber.hardLeft()
                        current_command = "hardLeft"
                    else:
                        saber.left()
                        current_command = "left"
                if abs(gamepad_data["yaw"]) < DEADZONE and abs(gamepad_data["thrust"]) < DEADZONE and abs(gamepad_data["vertical"]) < DEADZONE:
                    saber.stop()
                    current_command = None

                # Claw control (placeholder)
                if gamepad_data["claw"] != "neutral":
                    print(f"Claw command: {gamepad_data['claw']}")
                    await send_status(f"Claw: {gamepad_data['claw']}")

                # Log current state
                if current_command != last_command:
                    print(f"Executing: {current_command or 'stopped'}, Vertical: {gamepad_data['vertical']:.2f}, Thrust: {gamepad_data['thrust']:.2f}, Yaw: {gamepad_data['yaw']:.2f}, Claw: {gamepad_data['claw']}")
                    await send_status(f"Command: {current_command or 'stopped'}")
                    last_command = current_command

                await asyncio.sleep(1.0 / UPDATE_SPEED)

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            saber.stop()
            break

async def _startWebsocketWerver():
    print(f"Starting websocket on port {PORT}")
    async with websockets.serve(handleWebsocket, HOST, PORT):
        await asyncio.Future()

def start():
    asyncio.run(_startWebsocketWerver())
