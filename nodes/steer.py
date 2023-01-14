import evdev
import time
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)


mem_values = {"ABS_X":128 , "ABS_BRAKE" : 0, "ABS_GAS": 0}

device = evdev.InputDevice('/dev/input/event3')
print(device)
while True:
    time.sleep(0.5)
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
    print(mem_values)