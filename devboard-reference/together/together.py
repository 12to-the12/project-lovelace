from math import sin
from lcd import *


def main():
    imgWidth = 49
    imgHeight = 63
    x = 0
    xv = 1
    y = 0
    yv = 1
    lcd_init()
    lcd_clear()
    while True:
        lcd_fill(x - 1, y - 1, imgWidth + 2, 2) # TODO: not sure why I had to do height of 2 (should be 1) in order to avoid artifacts
        lcd_fill(x - 1, y + imgHeight, imgWidth + 2, 2) # TODO: not sure why I had to do height of 2 (should be 1) in order to avoid artifacts
        lcd_fill(x - 1, y + 1, 1, imgHeight - 1)
        lcd_fill(x + imgWidth, y + 1, 1, imgHeight - 1)
        lcd_blit_file("together.rgb", x, y, imgWidth, imgHeight)
        x += xv
        if x < 0:
            x = 0
            xv = -xv
        elif x + imgWidth >= width:
            x = width - imgWidth
            xv = -xv
        y += yv
        if y < 0:
            y = 0
            yv = -yv
        elif y + imgHeight >= height:
            y = height - imgHeight
            yv = -yv

if __name__ == "__main__":
    main()
