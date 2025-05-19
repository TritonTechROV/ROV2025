#!/usr/bin/env python3

'''
    MAIN FILE TO RUN!!!

    Starts the websocket, Flask, and sabertooths.

    Required libs: pip3 install websockets flask pyserial RPi.GPIO
'''

import threading
from flask import Flask, render_template, request, Response
import configparser
# Local imports
import websock
import webcam
import saber

config = configparser.ConfigParser()
config.read("config.ini")

SOCKPORT = config.getint("WEB", "sockport", fallback=8765)
PORT = config.getint("WEB", "webport", fallback=5000)
HOST = config.get("WEB", "host", fallback="127.0.0.1")

# Flask app with basic authentication
app = Flask(__name__)

def check_auth(username, password):
    return username == config.get("AUTH", "user", fallback="admin") and password == config.get("AUTH", "pass", fallback="admin")

def authenticate():
    return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'})

@app.route('/')
def index():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    return render_template("index.html", host=HOST, port=SOCKPORT)

@app.route('/feed/<cam_id>')
def feed(cam_id):
    if cam_id not in webcam.cameras:
        return Response("Camera not found", 404)
    else:
        return Response(webcam.cameras[cam_id].read(), mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    app.run(host=HOST, port=PORT, debug=True)

if __name__ == "__main__":
    thread = threading.Thread(target = main)
    thread.start()
    websock.start()
