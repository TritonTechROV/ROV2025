import cv2 
import sys
from flask import Flask, render_template, Response
from webcamvideostream import WebcamVideoStream
from flask_basicauth import BasicAuth
import time
import threading

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'rov'
app.config['BASIC_AUTH_PASSWORD'] = '123456789ab'
app.config['BASIC_AUTH_FORCE'] = True

basicAuth = BasicAuth(app)
last_epoch = 0

cameras = {
    "front": WebcamStream(src=0).start(),
    "back": WebcamStream(src=1).start(),
    "left": WebcamStream(src=2).start(),
    "right": WebcamStream(src=3).start()
}

@app.route('/')
@basicAuth.required
def index(): 
    return render_template('index.html')

def gen(camera):
    while True:        
        frame = camera.read()
            if frame is None:
                continue
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        

@app.route('/feed/<cam_id>')
def feed(cam_id):
    if cam_id not in cameras:
        return "Camera not found", 404
    return Response(gen(cameras[cam_id]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
