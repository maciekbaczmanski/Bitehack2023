import evdev
import paho.mqtt.client as mqtt
import time
import json
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)

mode = 'manual'

mem_values = {"ABS_X":128 , "ABS_BRAKE" : 0, "ABS_GAS": 0, "V":0, "M_L":0, "M_R":0}

device = evdev.InputDevice('/dev/input/event4')
broker_address = "172.16.25.128"
client = mqtt.Client()
# client.username_pw_set("Raspberry_Pi", "Rpi_Raspberry_Python")
# client.on_message = on_message
# client.connect(broker_address, 1883)
print(device)
while True:
    time.sleep(0.2)
    print("-------------------------")
    try:
        for event in device.read():
            print(evdev.categorize(event))
            # if event.type == evdev.ecodes.EV_KEY:
            if event.type == evdev.ecodes.EV_KEY:
                print(evdev.ecodes.EV_KEY[event.code])
            # print(evdev.ecodes.ABS[event.code])
            if event.type == evdev.ecodes.EV_ABS and evdev.ecodes.ABS[event.code] in mem_values.keys():
                mem_values[evdev.ecodes.ABS[event.code]] = event.value
                # print(evdev.categorize(event))
                # print(evdev.ecodes.ABS[event.code], " : ",event.value)
    except:
        pass
    if(mem_values["ABS_BRAKE"] * mem_values["ABS_GAS"] == 0):
        mem_values["V"] = (mem_values["ABS_BRAKE"] - mem_values["ABS_GAS"])/255
    # print("V: ",mem_values["V"])
    motor_l = 100
    motor_r = 100
    normalize_x = (200 * (mem_values["ABS_X"]-128))/255
    if normalize_x <0:
        motor_l -= abs(normalize_x)
    elif normalize_x >0:
        motor_r -= abs(normalize_x)
    
    mem_values["M_L"] = int(motor_l * mem_values["V"])
    mem_values["M_R"] = int(motor_r * mem_values["V"])
    if mode == 'manual':
        # print("LEFT: ",mem_values["M_L"]," RIGHT: ",mem_values["M_R"])
        MQTT_MSG=json.dumps({"L": str(mem_values["M_L"]),"R": str(mem_values["M_R"])})
        # client.publish("steer/motors", MQTT_MSG, qos=0, retain=False)




