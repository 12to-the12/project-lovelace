from random import randint, choice
from math import sqrt
from lcd import *


def sierpinski():
    points = [(0, 320 - 1), (480 / 2, 0), (480 - 1, 320 - 1)]
    x, y = points[0]
    while True:
        p = choice(points)
        xt, yt = p
        x = (xt + x) / 2
        y = (yt + y) / 2
        red = int((1 - distance(x, y, points[0]) / 480) * 256)
        green = int((1 - distance(x, y, points[1]) / 400) * 256)
        blue = int((1 - distance(x, y, points[2]) / 480) * 256)
        lcd_set_color(red, green, blue)
        # lcd_put(int(x), int(y), randint(0, int(y/320*256)), randint(0, int(x/480*256)), randint(0, int(x/480*256)))
        lcd_draw_pixel(int(x), int(y))


def distance(x, y, p):
    return sqrt((p[0] - x) ** 2 + (p[1] - y) ** 2)


# Run the code
lcd_init()
lcd_clear()
sierpinski()


def main():
    sierpinski()
