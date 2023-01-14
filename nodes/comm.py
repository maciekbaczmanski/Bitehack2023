from pygame import mixer  # Load the popular external library
import paho.mqtt.client as mqtt
import time
mixer.init()
mixer.music.load('ryszard.mp3')
broker_address = "172.16.25.128"
client = mqtt.Client()
# client.username_pw_set("Raspberry_Pi", "Rpi_Raspberry_Python")
# client.on_message = on_message
client.connect(broker_address, 1883)

def on_message(client, userdata, message):
    global bedroom_delay, switch_off
    if message.topic == "alarm":
        if str(message.payload.decode("utf-8")) == "start":
        # client.publish("test2", "ok", qos=0, retain=False)
            mixer.music.play(-1)
        elif str(message.payload.decode("utf-8")) == "stop":
            mixer.music.stop()

client.subscribe([("alarm", 0), ])


while True:
    time.sleep(1)