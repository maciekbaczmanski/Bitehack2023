import evdev
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)


mem_values = {"ABS_X":128 , "ABS_BRAKE" : 0, "ABS_GAS": 0}

device = evdev.InputDevice('/dev/input/event3')
print(device)
for event in device.read_loop():
    # if event.type == evdev.ecodes.EV_KEY:
    
    # print(evdev.ecodes.ABS[event.code])
    if event.type == evdev.ecodes.EV_ABS and evdev.ecodes.ABS[event.code] in mem_values.keys():
        mem_values[evdev.ecodes.ABS[event.code]] = event.value
        print(mem_values)
        # print(evdev.categorize(event))
        # print(evdev.ecodes.ABS[event.code], " : ",event.value)
