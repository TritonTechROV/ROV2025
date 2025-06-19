import asyncio
import websockets
import json
import configparser
import threading

import saber
import claw

config = configparser.ConfigParser()
config.read("config.ini")

UPDATE_SPEED = config.getint("WEB", "tickspeed", fallback=60)
PORT = config.getint("WEB", "sockport", fallback=8765)
DEADZONE = config.getfloat("CONTROL", "deadzone", fallback=0.1)
HOST = config.get("WEB", "host", fallback="127.0.0.1")
THRESHOLD = 0.5

def eStop():
    print("Stop command received")
    saber.stop()
    claw.set_command(claw.HOLD)

def parsePacket(message):
    if message.get("type") == "stop":
        eStop()
        return None
    elif message.get("type") == "gamepad":
        gamepad = {"vertical": 0.0, "yaw": 0.0, "thrust": 0.0, "claw": 0}
        gamepad.update({
            "vertical": float(message["vertical"]),
            "yaw": float(message["yaw"]),
            "thrust": float(message["thrust"]),
            "claw": int(message["claw"])
        })
        return gamepad
    return None

async def send_status(websocket, message):
    try:
        await websocket.send(json.dumps({"message": message}))
    except Exception as e:
        print(f"[send_status] {e}")

async def handleWebsocket(websocket):
    print("Client connected")
    last_claw = claw.HOLD

    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
                gamepad_data = parsePacket(data)

                if gamepad_data is None:
                    await send_status(websocket, "ROV stopped")
                    continue

                saber.deactivateAll()
                current_command = None

                print(gamepad_data)

                # Map gamepad data to Sabertooth commands
                if abs(gamepad_data["vertical"]) > DEADZONE:
                    if gamepad_data["vertical"] > 0:
                        saber.up()
                        current_command = "up"
                    else:
                        saber.down()
                        current_command = "down"
                elif abs(gamepad_data["vertical"]) <= DEADZONE: 
                    saber.stopupdown()
                if abs(gamepad_data["thrust"]) > DEADZONE:
                    if gamepad_data["thrust"] > 0: 
                        saber.forward()
                        current_command="forward"
                    else:
                        saber.backward()
                        current_command="backward"
                if abs(gamepad_data["yaw"]) > DEADZONE:
                    if gamepad_data["yaw"] > THRESHOLD:
                        saber.hardRight()
                        current_command = "hardRight"
                    elif gamepad_data["yaw"] > 0:
                        saber.right()
                        current_command = "right"
                    elif gamepad_data["yaw"] < -THRESHOLD:
                        saber.hardLeft()
                        current_command = "hardLeft"
                    else:
                        saber.left()
                        current_command = "left"
                if abs(gamepad_data["thrust"]) <= DEADZONE and abs(gamepad_data["yaw"]) <= DEADZONE:
                    saber.stopforwardback()
                if abs(gamepad_data["yaw"]) < DEADZONE and abs(gamepad_data["thrust"]) < DEADZONE and abs(gamepad_data["vertical"]) < DEADZONE:
                    saber.stop()
                    current_command = None

 # Claw
                if gamepad_data["claw"] != last_claw:
                    claw.set_command(gamepad_data["claw"])
                    last_claw = gamepad_data["claw"]

                await send_status(websocket, f"Command: {current_command or 'idle'}, Claw: {last_claw}")
                await asyncio.sleep(1 / UPDATE_SPEED)

            except Exception as e:
                print(f"[handleWebsocket:inner] {e}")
                continue

    except websockets.exceptions.ConnectionClosed:
        print("WebSocket disconnected")
        eStop()

async def _startWebsocketServer():
    print(f"WebSocket server running on {HOST}:{PORT}")
    async with websockets.serve(handleWebsocket, HOST, PORT):
        await asyncio.Future()

def start():
    threading.Thread(target=claw.control_claw, daemon=True).start()
    asyncio.run(_startWebsocketServer())
