import cv2
from threading import Thread
import time

import configparser
config = configparser.ConfigParser()
config.read("config.ini")

class WebcamStream:
    def __init__(self, src =0):
        print(f"Initializing camera {src}")
        self.src = src
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            print(f"Camera {src} could not be opened!")
        self.stopped = False

    def read(self):
        while True:
            success, frame = self.stream.read()
            if not success or frame is None:
                print(f"[WARNING] Failed to read frame from camera {self.src}")
                time.sleep(0.1)
                continue
    
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print(f"[WARNING] Failed to encode frame from camera {self.src}")
                time.sleep(0.1)
                continue
    
            frame = buffer.tobytes()
    
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



    def stop(self):
        print(f"Releasing camera {self.src}")
        self.stopped = True
        self.stream.release()

cameras = {
    "front": WebcamStream(src=config.get("CAMS", "front")),
    "back": WebcamStream(src=config.get("CAMS", "back")),
    "left": WebcamStream(src=config.get("CAMS", "left")),
    "right": WebcamStream(src=config.get("CAMS", "right"))
}
