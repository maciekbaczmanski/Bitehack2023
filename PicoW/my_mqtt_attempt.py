import mqtt

client_id = 'toDurnePico2'
mqtt_server = 'picztery.local'
client = mqtt.MQTTClient(client_id, mqtt_server, keepalive=3600)

import network
SSID = 'MamNaCiebieOko'
PASSWD = 'Niezgadniesz.'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWD)
wlan.isconnected()
wlan.status()
mqtt_server = '172.16.25.128'
client_id = 'toDurnePico2'
client = mqtt.MQTTClient(client_id, mqtt_server, keepalive=3600)
client.connect()
def msgCallback(topic, message):
    print("Topic: ", topic)
    print("Message: ", message)
    
client.set_callback(msgCallback)
client.subscribe('chujWDupe')

while True:
    client.wait_msg()
