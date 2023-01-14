import wifi as WiFi
from mqtt import MQTTClient

from motor import Motor
import json

mqtt_server = '172.16.25.128'
client_id = 'motorDriver'
motor_topic = 'steer/motors'

msg_counter_full = 3000
msg_counter_diff = 500
msg_counter = 0

motor2 = Motor(0, 1)
motor1 = Motor(2, 3)

def msgCallback(topic, message):
    global msg_counter
    print(topic.decode('ascii'), message.decode('ascii'))
    if topic.decode('ascii') == motor_topic:
        print("Message: ", message)
        motor_speeds = json.loads(message.decode('ascii'))
        motor1.run(int(motor_speeds["L"]))
        motor2.run(int(motor_speeds["R"]))
        msg_counter = msg_counter_full

wifi = WiFi.connect()

client = MQTTClient(client_id, mqtt_server, keepalive=3600)
client.connect()
client.set_callback(msgCallback)
client.subscribe(motor_topic)

def mqttReceiveLoop():
    while True:
        client.wait_msg()

from utime import sleep_ms
import _thread

def watchdog_loop():
    while True:
        global msg_counter
        msg_counter -= msg_counter_diff
        if msg_counter < 0:
            motor1.run(0)
            motor2.run(0)
            print("Motors stopped due to controller inactivity")
        sleep_ms(msg_counter_diff)

_thread.start_new_thread(watchdog_loop, ())
mqttReceiveLoop()

