from machine import ADC, Pin, PWM, SPI

joy_x = ADC(Pin(26, pull=None))
joy_y = ADC(Pin(27, pull=None))


class Joystick:
    def __init__(self):
        pass

    @property
    def x(self):
        x = (joy_x.read_u16() / 2**16 - 0.5) * 2
        return x**3

    @property
    def y(self):
        y = (joy_y.read_u16() / 2**16 - 0.5) * 2
        return -(y**3)

    def read(self):
        return (self.x, self.y)


joystick = Joystick()
