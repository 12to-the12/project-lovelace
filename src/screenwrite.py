from lcd import *
from sprite import world
from random import randint

col_start = randint(10, 120)
col = col_start
row = randint(10, 120)


def printsc(text="", end="\n"):
    global row, col

    text = text.upper()
    text += end
    for char in text:
        print(char, end="")
        if col >= 400:
            col = col_start
            row += 12
        if char == "\n":
            col = col_start
            row += 12

        else:
            lcd_draw_char(col, row, char)
            col += 6

    # lcd_clear()
