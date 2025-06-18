#!/usr/bin/env python3

import asyncio
import websockets
import json
import configparser
import threading

# Local modules
import saber
import claw

# Load config
config = configparser.ConfigParser()
config.read("config.ini")

UPDATE_SPEED = config.getint("WEB", "tickspeed", fallback=60)
PORT = config.getint("WEB", "sockport", fallback=8765)
DEADZONE = config.getfloat("CONTROL", "deadzone", fallback=0.1)
HOST = config.get("WEB", "host", fallback="127.0.0.1")

def eStop():
    print("Stop command received")
    saber.stop()
    claw.set_command(claw.HOLD)

def parsePacket(message):
    if message["type"] == "stop":
        eStop()
        return None
    elif message["type"] == "gamepad":
        return {
            "vertical": float(message["vertical"]),
            "yaw": float(message["yaw"]),
            "thrust": float(message["thrust"]),
            "claw": int(message["claw"])
        }
    return None

async def send_status(websocket, message):
    try:
        await websocket.send(json.dumps({"message": message}))
    except:
        pass

async def handleWebsocket(websocket):
    print("Client connected")
    last_command = None

    while True:
        try:
            async for message in websocket:
                data = json.loads(message)
                gamepad_data = parsePacket(data)
                if gamepad_data is None:
                    await send_status(websocket, "ROV stopped")
                    continue

                saber.deactivateAll()
                cmd = None

                # Movement handling
                if abs(gamepad_data["vertical"]) > DEADZONE:
                    cmd = "up" if gamepad_data["vertical"] > 0 else "down"
                    getattr(saber, cmd)()
                else:
                    saber.stopupdown()

                if abs(gamepad_data["thrust"]) > DEADZONE:
                    cmd = "forward" if gamepad_data["thrust"] > 0 else "backward"
                    getattr(saber, cmd)()
                else:
                    saber.stopforwardback()

                if abs(gamepad_data["yaw"]) > DEADZONE:
                    if gamepad_data["yaw"] > 0.5:
                        saber.hardRight()
                        cmd = "hardRight"
                    elif gamepad_data["yaw"] > 0:
                        saber.right()
                        cmd = "right"
                    elif gamepad_data["yaw"] < -0.5:
                        saber.hardLeft()
                        cmd = "hardLeft"
                    else:
                        saber.left()
                        cmd = "left"

                if all(abs(gamepad_data[k]) <= DEADZONE for k in ["yaw", "thrust", "vertical"]):
                    saber.stop()

                # Claw control
                claw.set_command(gamepad_data["claw"])

                await send_status(websocket, f"Command: {cmd or 'stopped'}, Claw: {gamepad_data['claw']}")
                print(f"> {cmd or 'stopped'} | V:{gamepad_data['vertical']} T:{gamepad_data['thrust']} Y:{gamepad_data['yaw']} C:{gamepad_data['claw']}")

                await asyncio.sleep(1 / UPDATE_SPEED)

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket disconnected")
            eStop()
            break

async def _startWebsocketServer():
    print(f"WebSocket server running on {HOST}:{PORT}")
    async with websockets.serve(handleWebsocket, HOST, PORT):
        await asyncio.Future()

def start():
    # Start claw in background
    threading.Thread(target=claw.control_claw, daemon=True).start()
    asyncio.run(_startWebsocketServer())
