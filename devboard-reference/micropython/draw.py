from utime import sleep
from urandom import randint
from lcd import *

size = 5
def play():
    x = width / 2
    y = height / 2
    speed = 8
    lcd_set_color(255, 255, 255)
    while True:
        jx = (joy_x.read_u16() / 2**16 - .5) * speed
        jy = (joy_y.read_u16() / 2**16 - .5) * speed
        if sqrt(jx*jx + jy*jy) < .1 * speed:
            jx = 0
            jy = 0
        x += jx
        y -= jy
        if x < 0:
            x = 0
        elif x >= width - 1 - size:
            x = width - 1 - size
        if y < 1:
            y = 1
        elif y >= height - 1 - size:
            y = height - 1 - size

        lcd_fill(int(x), int(y), size, size)
        if not button_a.value():
            lcd_set_color(randint(0, 255),randint(0, 255),randint(0, 255))
        if not button_b.value():
            lcd_clear(randint(0, 255),randint(0, 255),randint(0, 255))
        # if not button_a() and not button_b.value():
        # print(f'{x=}, {y=}')

        sleep(.01)

lcd_init()
lcd_clear(0,5,0)
play()