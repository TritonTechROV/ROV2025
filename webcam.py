import cv2
from threading import Thread
import threading
import time
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

class WebcamStream:
    def __init__(self, src =0):
        print(f"Initializing camera {src}")
        self.src = int(src)
        self.stream = cv2.VideoCapture(self.src)

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.stream.set(cv2.CAP_PROP_FPS, 15)
        
        if not self.stream.isOpened():
            print(f"Camera {src} could not be opened!")
        self.stopped = False
        self.frame = None
        self.lock = threading.Lock()
        
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()
    def update(self):
        while not self.stopped:
            success, frame = self.stream.read()
            if success:
                with self.lock:
                    self.frame = frame
            time.sleep(0.03)

    def read(self):
        while not self.stopped:
            with self.lock:
                if self.frame is not None:
                    ret, buffer = cv2.imencode('.jpg', self.frame)
                    frame = buffer.tobytes()
                    yield(b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.03)


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
