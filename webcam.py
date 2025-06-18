import cv2
import time
import configparser

# Load camera config
config = configparser.ConfigParser()
config.read("config.ini")

class WebcamStream:
    def __init__(self, src=0):
        self.src = int(src)  # ensure it's an integer index
        print(f"Initializing camera {self.src}")
        self.stream = cv2.VideoCapture(self.src)

        if not self.stream.isOpened():
            print(f"[ERROR] Camera {self.src} could not be opened!")
        
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

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def stop(self):
        print(f"Releasing camera {self.src}")
        self.stopped = True
        self.stream.release()

# Initialize all cameras from config
cameras = {
    "front": WebcamStream(src=config.get("CAMS", "front")),
    "back":  WebcamStream(src=config.get("CAMS", "back")),
    "left":  WebcamStream(src=config.get("CAMS", "left")),
    "right": WebcamStream(src=config.get("CAMS", "right"))
}
