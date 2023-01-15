from machine import Pin, PWM
from time import sleep

pwm11 = PWM(Pin(0))
pwm12 = PWM(Pin(1))

pwm11.freq(1000)
pwm12.freq(1000)

while True:
    pwm12.duty_u16(0)
    for duty in range(65025):
        pwm11.duty_u16(duty)
        sleep(0.0001)
    for duty in range(65025, 0, -1):
        pwm11.duty_u16(duty)
        sleep(0.0001)
    pwm11.duty_u16(0)
    for duty in range(65025):
        pwm12.duty_u16(duty)
        sleep(0.0001)
    for duty in range(65025, 0, -1):
        pwm12.duty_u16(duty)
        sleep(0.0001)
    pwm11.duty_u16(0)
    pwm12.duty_u16(0)
    sleep(1)
