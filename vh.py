import cv2
from flask import Flask, render_template, Response
# from flask_apscheduler import APScheduler
from threading import Thread, Condition
import numpy as np
from flask_mqtt import Mqtt
import json


## FRAME GRABBING
class VideoCapture(Thread):
    res = (640, 320)
    dummy_frame = np.zeros(res + (3,), dtype=np.uint8)

    def __init__(self):
        Thread.__init__(self)
        cap = cv2.VideoCapture(0, cv2.CAP_V4L)
        self.video = cap

        self.frame = self.dummy_frame
        # self.frame_enc = self.enc_frame(self.dummy_frame)
        self.frame_id = 0
        self.frame_lock = Condition()
        self.subs = [9999, 9999]
    
    def __del__(self):
        self.video.release()

    @staticmethod
    def enc_frame(frame, dummy=None):
        try:
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        except:
            try:
                ret, jpeg = cv2.imencode('.jpg', dummy)
                return jpeg.tobytes()
            except:
                ret, jpeg = cv2.imencode('.jpg', frame)
                return jpeg.tobytes()

    def update_frame(self):
        # extracting frames
        with self.frame_lock: 
            self.frame_lock.wait_for( lambda : (
                    self.subs[0] >= self.frame_id
                and self.subs[1] >= self.frame_id
            ), timeout=.05)
            ret, frame = self.video.read()
            if not np.size(frame): frame = self.dummy_frame
            self.frame = frame 
            # self.frame_enc = self.enc_frame(frame, self.dummy_frame)

            self.frame_id += 1
            self.frame_lock.notify()
            # print("")
            # print("0", end="") #dg

    def run(self): # thread target
        while True:
            self.update_frame()

    def sync_frame(self, sub_id, skip_factor=0):
        last_frame_id = self.frame_id
        while True: 
            # print("SK", self.frame_id, last_frame_id, skip_factor) # dg
            with self.frame_lock: 
                self.frame_lock.wait_for(
                    lambda : self.frame_id > last_frame_id + skip_factor)
                # print("1", end="") #dg
                yield None
                last_frame_id = self.frame_id
                self.subs[sub_id] = last_frame_id + skip_factor
            
vcap_t = VideoCapture()

## ONBOARD ANALYSIS
class PopePursue(Thread):
    skip_frame_f = 2
    res = (640, 800)
    area_th = 60 #res[0]*res[1] / 120
    w_th = 60
    h_th = 60
    dummy_frame = np.zeros(res + (3,), dtype=np.uint8)
    bb_color = (255, 0, 0)
    bb_thick = 10
    max_throttle = 80
    min_throttle = 55

    @staticmethod
    def img_metric(frame): # to be parametrized
        try:
            fhsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).swapaxes(0, 2)
        except:
            fhsv = cv2.cvtColor(vcap_t.dummy_frame, cv2.COLOR_RGB2HSV).swapaxes(0, 2)
        return np.logical_and(
            np.logical_and(90  < fhsv[0], fhsv[0] < 105),
            np.logical_and(
                100 < fhsv[1],
                np.logical_and(70 < fhsv[2], fhsv[2] < 170)
            )
        ).swapaxes(0, 1).astype(np.uint8) * 255

    def __init__(self):
        Thread.__init__(self)
        self.frame_enc = vcap_t.enc_frame(self.dummy_frame)
        self.bb = None
        self.autoc = False

    @staticmethod
    def draw_rectangle(img, x, y, w, h, c, t):
        img[y:(y+h), (x+(w//2)-t):(x+(w//2)+t)] = c
        img[(y+(h//2)-t):(y+(h//2)+t), x:(x+w)] = c

    def send_steering(cls, bb):
        if cls.autoc:
            if bb is not None:
                x = bb[0]
                w = bb[2]
                cx = x + w//2

                if cx < cls.res[1]//3: # person to the left
                    r = cls.max_throttle
                    l = cls.min_throttle
                elif cx > (cls.res[1]*2)//3:
                    r = cls.min_throttle
                    l = cls.max_throttle
                else:
                    r = cls.max_throttle
                    l = cls.max_throttle
            else:
                l = 0
                r = 0

            MQTT_MSG=json.dumps({"L": str(l), "R": str(r)})
            mqtt_client.publish("steer/motors", MQTT_MSG, qos=0, retain=False)

    def run(self):
        for _ in vcap_t.sync_frame(sub_id=0, skip_factor=self.skip_frame_f):
            # print("2", end="") #dg
            frame = vcap_t.frame
            # print("IMM", np.max(frame), np.min(frame)) #dg
            if not np.size(frame): continue
            try:
                frame = cv2.resize(frame, self.res)
            except: pass
            immet = self.img_metric(frame)

            contours, hierarchy = cv2.findContours(
                immet, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            
            if np.size(contours):
                c = max(contours, key=cv2.contourArea)
                ca = cv2.contourArea(c)
                if (ca > self.area_th):
                    x,y,w,h = cv2.boundingRect(c)
                    h = h//2
                    if w > self.w_th and h > self.h_th:
                        # self.draw_rectangle(immet, x, y, w, h, 255, 8)
                        # print("(", x, y, w, h, ca, ")")
                        self.bb = (x,y,w,h)
                    else: self.bb = None
                else: self.bb = None
            else: self.bb = None
            self.send_steering(self.bb)

            self.frame_enc = vcap_t.enc_frame(immet, self.dummy_frame)
            
ppur_t = PopePursue()

## MQTT
MA_CONFIG = {
    "MQTT_BROKER_URL": "172.16.25.128",
    "MQTT_BROKER_PORT": 1883,
    "MQTT_USERNAME": "wizja",
    "MQTT_PASSWORD": "",
    "MQTT_KEEPALIVE": 30,
    "MQTT_TLS_ENABLED": False,
}

mqtt_client = Mqtt()

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       mqtt_client.subscribe("#") # subscribe topic
   else:
        pass # print('Bad connection. Code:', rc)

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    topic=message.topic
    content=message.payload.decode() #'ASCII')

    if type(topic) is tuple:
        topic = ''.join(topic)

    if topic == "steer/mode":
        if content == "manual":
            ppur_t.autoc = False
        elif content == "auto":
            ppur_t.autoc = True

    # print(topic, content)


## STREAM
app = Flask(__name__)
app.config.from_mapping(
    **MA_CONFIG
)

def gen_frame_enc_frame():
    for _ in vcap_t.sync_frame(sub_id=1, skip_factor=0):
        frame = vcap_t.frame
        if ppur_t.bb:
            try:
                ppur_t.draw_rectangle(frame, *ppur_t.bb, 
                ppur_t.bb_color, ppur_t.bb_thick)
            except: pass

    # for _ in vcap_t.sync_frame(sub_id=1, skip_factor=ppur_t.skip_frame_f):
    #     frame = ppur_t.frame_enc #dg
        frame = vcap_t.enc_frame(frame, None)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frame_enc_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # threads
    vcap_t.start()
    ppur_t.start()

    mqtt_client.init_app(app)
    # defining server ip address and port
    app.run(host='0.0.0.0',port='5000', debug=False, use_reloader=False)

# # scp ./vid_cs.py pi@172.16.25.128:/home/pi/wizja/
# # libcamerify python3 vid_cs.py
# https://stackoverflow.com/questions/61047207/opencv-videocapture-does-not-work-in-flask-project-but-works-in-basic-example
