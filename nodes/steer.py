import evdev
import time
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)


mem_values = {"ABS_X":128 , "ABS_BRAKE" : 0, "ABS_GAS": 0, "V":0, "M_L":0, "M_R":0}

device = evdev.InputDevice('/dev/input/event3')
print(device)
while True:
    time.sleep(0.1)
    print("-------------------------")
    try:
        for event in device.read():
            # if event.type == evdev.ecodes.EV_KEY:
            
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
    
    mem_values["M_L"] = motor_l * mem_values["V"]
    mem_values["M_R"] = motor_r * mem_values["V"]
    print(mem_values)



