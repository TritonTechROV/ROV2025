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

def eStop():
    print("Stop command received")
    saber.stop()
    claw.set_command(claw.HOLD)

def parsePacket(message):
    if message.get("type") == "stop":
        eStop()
        return None
    elif message.get("type") == "gamepad":
        return {
            "vertical": float(message.get("vertical", 0)),
            "yaw": float(message.get("yaw", 0)),
            "thrust": float(message.get("thrust", 0)),
            "claw": int(message.get("claw", claw.HOLD))
        }
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

                # Movement - Vertical
                if abs(gamepad_data["vertical"]) > DEADZONE:
                    if (gamepad_data["vertical"] > 0):
                        saber.up()
                        current_command = "up"
                    else:
                        saber.down()
                        current_command = "down"
                else:
                    saber.stopupdown()

                 # Movement - Thrust
                if abs(gamepad_data["thrust"]) > DEADZONE:
                    if (gamepad_data["thrust"] > 0):
                        saber.forward()
                        current_command = "forward"
                    else:
                        saber.backward()
                        current_command = "backward"
                else:
                    saber.stopforwardback()

 # Movement - Yaw
                if abs(gamepad_data["yaw"]) > DEADZONE:
                    if gamepad_data["yaw"] > 0.5:
                        saber.hardRight()
                        current_command = "hardRight"
                    elif gamepad_data["yaw"] > 0:
                        saber.right()
                        current_command = "right"
                    elif gamepad_data["yaw"] < -0.5:
                        saber.hardLeft()
                        current_command = "hardLeft"
                    else:
                        saber.left()
                        current_command = "left"
                else:
                    saber.stop()




 # Claw
                if gamepad_data["claw"] != last_claw:
                    claw.set_command(gamepad_data["claw"])
                    last_claw = gamepad_data["claw"]

                await send_status(websocket, f"Command: {','.join(current_command) or 'idle'}, Claw: {last_claw}")
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
