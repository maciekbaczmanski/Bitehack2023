from rc522 import MFRC522
import utime
from mqtt import MQTTClient
import wifi as WiFi

reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0)

mqtt_server = '172.16.25.128'
client_id = 'pico_zaplon'
alarm_topic = 'alarm'

add_card_topic = 'add_card'
adding_card_mode = False

def msgCallback(topic, message):
    global adding_card_mode
    print("Topic: ", topic.decode('ascii'))
    print("Message: ", message.decode('ascii'))
    if topic.decode('ascii') == add_card_topic:
        if message.decode('ascii') == 'start':
            adding_card_mode = True
            print('Started adding card mode')
        else:
            adding_card_mode = False
            print('Ended adding card mode')

AdminUID = 2540327107
valid_uid_list = [AdminUID]

def read_card():
    reader.init()
    card = None
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            card = int.from_bytes(bytes(uid),"little",False)
            print("CARD ID: "+str(card))
            return card

wifi = WiFi.connect()

client = MQTTClient(client_id, mqtt_server, keepalive=3600)
client.connect()
client.set_callback(msgCallback)
client.subscribe(add_card_topic)

while True:
    card = read_card()
    if card:
        if adding_card_mode:
            valid_uid_list.append(card)
            print('Added new card')
        elif card in valid_uid_list:
            print("Gitara")
            client.publish(alarm_topic, "stop")
        else:
            print("ALARM")
            client.publish(alarm_topic, "start")
    client.check_msg()
    utime.sleep_ms(300)
