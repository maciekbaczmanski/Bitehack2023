import wifi as WiFi
from mqtt import MQTTClient

from motor import Motor
import json

mqtt_server = '172.16.25.128'
client_id = 'motorDriver'
motor_topic = 'steer/motors'

motor2 = Motor(0, 1)
motor1 = Motor(2, 3)

def msgCallback(topic, message):
    print(topic.decode('ascii'), message.decode('ascii'))
    if topic.decode('ascii') == motor_topic:
        print("Message: ", message)
        motor_speeds = json.loads(message.decode('ascii'))
        motor1.run(int(motor_speeds["L"]))
        motor2.run(int(motor_speeds["R"]))

wifi = WiFi.connect()

client = MQTTClient(client_id, mqtt_server, keepalive=3600)
client.connect()
client.set_callback(msgCallback)
client.subscribe(motor_topic)

while True:
    client.wait_msg()

