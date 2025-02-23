from config import config
from machine import ADC, Pin, PWM, SPI


joy_x = ADC(Pin(26, pull=None))
joy_y = ADC(Pin(27, pull=None))


button_a = Pin(15, Pin.IN)
button_b = Pin(14, Pin.IN)


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


def readdesktopinput():
    import pygame

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            # sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left = True
            if event.key == pygame.K_RIGHT:
                right = True
            if event.key == pygame.K_UP:
                up = True
            if event.key == pygame.K_DOWN:
                down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left = False
            if event.key == pygame.K_RIGHT:
                right = False
            if event.key == pygame.K_UP:
                up = False
            if event.key == pygame.K_DOWN:
                down = False

        if right:
            x = 1
        if left:
            x = -1
        if right and left:
            x = 0
        if (not right) and (not left):
            x = 0

        if down:
            y = 1
        if up:
            y = -1
        if down and up:
            y = 0
        if (not up) and (not down):
            y = 0
        return (x, y)


def readinputboard():
    return joystick.read(), not button_a.value(), not button_b.value()


if config.desktop_mode:
    readinput = readdesktopinput
else:
    readinput = readinputboard
