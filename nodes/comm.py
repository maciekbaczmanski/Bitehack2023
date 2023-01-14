from pygame import mixer  # Load the popular external library
import paho.mqtt.client as mqtt
import time
import telepot
from telepot.loop import MessageLoop


mixer.init()
mixer.music.load('ryszard.mp3')
broker_address = "172.16.25.128"
client = mqtt.Client()
# client.username_pw_set("Raspberry_Pi", "Rpi_Raspberry_Python")
# client.on_message = on_message


def on_message(client, userdata, message):
    global bedroom_delay, switch_off
    if message.topic == "alarm":
        if str(message.payload.decode("utf-8")) == "start":
        # client.publish("test2", "ok", qos=0, retain=False)
            mixer.music.play(-1)
        elif str(message.payload.decode("utf-8")) == "stop":
            mixer.music.stop()

client.on_message = on_message
client.connect(broker_address, 1883)
client.loop_start()
client.subscribe([("alarm", 0), ])




class Telegram:
    def __init__(self,token):
        print(token)
        print("aa")
        self.bot = telepot.Bot(token)
        # self.permissions = [1255224844, 1990072643]
        self.permissions = []
        MessageLoop(self.bot, self.handle).run_as_thread()

    def msg_me(self, message):
        self.bot.sendMessage(1255224844, message)

    def msg_all(self, message):
        for ID in self.permissions:
            self.bot.sendMessage(ID, message)

    def handle(self, msg):
        if msg['from']['id'] in self.permissions:
            if '/ping' in msg['text']:
                self.bot.sendMessage(msg['from']['id'], 'Pong!')
            elif '/add' in msg['text'] and len(msg['text']) > 5:
                try:
                    toadd = int(msg['text'].replace('/add ', ''))
                    self.permissions.append(toadd)
                    self.bot.sendMessage(msg['from']['id'], 'User added!')
                except:
                    self.bot.sendMessage(msg['from']['id'], 'Unknown error while adding user!')
            else:
                self.msg_all(
                    'Wrong message! If want to respond to last email, type:\nSPACE,BUILDING   (example: 05,9A)\nnone  <- for custom without space&building')
        else:
            self.bot.sendMessage(msg['from']['id'],
                                 'No permisions! Ask admin to add your ID.\nYour ID:\n' + str(msg['from']['id']))


token=open("/home/pi/token.txt").read()
bocik = Telegram(token)
# bocik.msg_all('Service starting after system restart!\n For help type: /help')

while True:
    time.sleep(1)