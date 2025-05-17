import cv2
from threading import Thread
import time
import numpy as np

class WebcamStream:
    def __init__(self, src =0):
        print(f"[INFO] Initializing camera {src}")
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            raise RuntimeError(f"Camera {src} could not be opened.")
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False
        time.sleep(2.0)

    def start(self):
        print("[INFO] Starting camera thread")
        t = Thread(target=self.update, daemon = True)
        t.start()
        return self

    def update(self):
        print("read")
        while not self.stopped:
                self.grabbed, self.frame = self.stream.read()

     def read(self):
        return self.frame
    
    def stop(self):
        print("[INFO] Releasing camera")
        self.stopped = True
        self.stream.release()