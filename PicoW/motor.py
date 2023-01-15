from machine import Pin, PWM

class Motor:
    def __init__(self, pin1, pin2):
        self.pinId1 = pin1
        self.pinId2 = pin2
        self.__max_duty__ = 65025
        
        self.pwm1 = PWM(Pin(self.pinId1))
        self.pwm2 = PWM(Pin(self.pinId2))
        
        self.pwm1.freq(1000)
        self.pwm2.freq(1000)
        
        self.pwm1.duty_u16(0)
        self.pwm2.duty_u16(0)
    
    def run(self, speed):
        duty = self.__get_duty__(speed)
        
        if speed == 0:
            self.pwm1.duty_u16(0)
            self.pwm2.duty_u16(0)
        elif speed > 0:
            self.pwm1.duty_u16(duty)
            self.pwm2.duty_u16(0)
        else:
            self.pwm1.duty_u16(0)
            self.pwm2.duty_u16(-1 * duty)
    
    def __get_duty__(self, pwm):
        return int(pwm * self.__max_duty__ / 100)

