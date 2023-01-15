from machine import Pin
import time

m11 = Pin(0, Pin.OUT)
m12 = Pin(1, Pin.OUT)

while True:
    m11.value(0)
    m12.value(1)
    time.sleep(1)
    m11.value(1)
    m12.value(0)
    time.sleep(1)
    m11.value(0)
    time.sleep(1)
