# Copyright (c) 2025 by Alfred Morgan <alfred@54.org>
# Copyright (c) 2025 by Mitchell Tucker
# Copyright (c) 2025 by Logan Hillyer
# License https://opensource.org/license/isc-license-txt
# ST7796SU1 https://www.displayfuture.com/Display/datasheet/controller/ST7796s.pdf
# Version: 0.0.4

from machine import ADC, Pin, PWM, SPI
from utime import sleep
from urandom import randint
from math import sqrt
from neopixel import NeoPixel

np = NeoPixel(Pin(12, Pin.OUT), 1)
beeper = PWM(13)
spi = SPI(0, baudrate=-1, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
Pin(5, Pin.OUT or Pin.PULL_DOWN)  # Chip select (pull down for dedicated spi)
dc = Pin(6, Pin.OUT)  # Data / Command
rst = Pin(7, Pin.OUT)  # Reset
joy_x = ADC(Pin(26, pull=None))
joy_y = ADC(Pin(27, pull=None))
button_a = Pin(15, Pin.IN)
button_b = Pin(14, Pin.IN)
width = 480
height = 320
r = 0
g = 0
b = 0


def lcd_rgb_led(r, g, b):
    np[0] = (r, g, b)
    np.write()


@micropython.viper
def lcd_command(cmd):
    # dc is pin6
    # spi
    # sck is pin2
    # mosi is pin3
    # miso is pin4
    # base = ptr32(0x40028000)
    # sck =
    dc.value(0)  # Instruction mode
    spi.write(bytearray([cmd]))


@micropython.native
def lcd_data(data):
    dc.value(1)  # Parameter mode
    spi.write(bytearray([data]))


def lcd_reset():
    rst.value(0)
    sleep(0.12)
    rst.value(1)
    sleep(0.12)


@micropython.native
def lcd_call(f, *p):
    lcd_command(f)
    if p:
        for par in p:
            lcd_data(par)
        # dc.value(1)  # Parameter mode
        # spi.write(bytearray(p))


def lcd_init():
    lcd_reset()
    # lcd_command(0x01) # soft reset
    lcd_command(0x11)  # Sleep out
    sleep(0.12)
    lcd_call(0x36, 0x28)  # Memory Access Control top-down BGR order
    lcd_call(0x3A, 0x07)  # Set to 24-bit color mode (RGB888)
    # lcd_call(0x3A, 0x06)  # Set to 18-bit color mode (RGB666)
    # lcd_call(0x3A, 0x05)  # Set to 16-bit color mode (RG565)
    lcd_command(0x21)  # invert colors
    sleep(0.12)
    lcd_command(0x29)  # Display ON


def lcd_set_color(_r, _g, _b):
    global r, g, b
    r = _r
    g = _g
    b = _b


def lcd_clear(r=0, g=0, b=0):
    lcd_set_range(0, 0, width, height)
    lcd_draw()
    row = bytearray([r, g, b] * width)
    for _ in range(height):
        spi.write(row)


@micropython.native
def lcd_fill(x: int, y: int, w: int, h: int):
    # set write range
    lcd_set_range(x, y, w, h)
    # lcd_set_range_fast(x, y, w, h)
    # initiate memory write
    lcd_draw()
    # write rows to display
    # row = bytearray()
    # for _ in range(w):
    #     row.append(r)
    #     row.append(g)
    #     row.append(b)
    #     row.extend([r, g, b])
    # row = bytearray(mylist)
    row = bytearray([r, g, b] * w)
    write_bytes(row, h)


@micropython.viper
def write_bytes(row, h: int):
    write = spi.write
    for i in range(h):
        write(row)


def lcd_read_data(num_bytes=1):
    dc.value(1)  # Data mode
    response = spi.read(num_bytes)
    return response


# @micropython.viper
# def lcd_set_range_fast(x: int, y: int, w: int, h: int):
#     w -= 1
#     h -= 1
#     dc.value(0)  # Instruction mode
#     spi.write(bytearray([0x2A]))
#     dc.value(1)  # Parameter mode
#     spi.write(bytearray([x >> 8 & 0xFF]))
#     spi.write(bytearray([x & 0xFF]))
#     spi.write(bytearray([x + w >> 8 & 0xFF]))
#     spi.write(bytearray([x + w & 0xFF]))

#     dc.value(0)  # Instruction mode
#     spi.write(bytearray([0x2B]))
#     dc.value(1)  # Parameter mode
#     spi.write(bytearray([y >> 8 & 0xFF]))
#     spi.write(bytearray([y & 0xFF]))
#     spi.write(bytearray([y + h >> 8 & 0xFF]))
#     spi.write(bytearray([y + h & 0xFF]))


@micropython.native
def lcd_set_range(x: int, y: int, w: int, h: int):
    w -= 1
    h -= 1
    lcd_call(0x2A, x >> 8 & 0xFF, x & 0xFF, x + w >> 8 & 0xFF, x + w & 0xFF)
    lcd_call(0x2B, y >> 8 & 0xFF, y & 0xFF, y + h >> 8 & 0xFF, y + h & 0xFF)


# initiates memory write
@micropython.native
def lcd_draw():
    lcd_command(0x2C)
    dc.value(1)  # Data mode


def lcd_draw_pixel(x, y):
    x_high = x >> 8 & 0xFF
    x_low = x & 0xFF
    y_high = y >> 8 & 0xFF
    y_low = y & 0xFF
    lcd_command(0x2A)  # Column address set
    lcd_data(x_high)
    lcd_data(x_low)
    lcd_data(x_high)
    lcd_data(x_low)

    lcd_command(0x2B)  # Row address set
    lcd_data(y_high)
    lcd_data(y_low)
    lcd_data(y_high)
    lcd_data(y_low)

    # Begin writing to memory
    lcd_command(0x2C)  # Memory write
    dc.value(1)  # Data mode
    spi.write(bytearray([r, g, b]))


def lcd_draw_h_line(x1, y, x2):
    w = x2 - x1
    if w >= 0:
        lcd_fill(x1, y, w, 1)
    else:
        lcd_fill(x2, y, -w, 1)


def lcd_draw_v_line(x, y1, y2):
    h = y2 - y1
    if h >= 0:
        lcd_fill(x, y1, 1, h)
    else:
        lcd_fill(x, y2, 1, -h)

def lcd_draw_line(x1, y1, x2, y2):
    """
    Draw a line from (x1, y1) to (x2, y2).
    Uses direct fills for horizontal/vertical lines,
    and a Bresenham-like approach for all other lines.
    """
    
    # 1) Purely horizontal line
    if y1 == y2:
        w = x2 - x1
        if w >= 0:
            lcd_fill(x1, y1, w, 1)
        else:
            lcd_fill(x2, y1, -w, 1)
        return

    # 2) Purely vertical line
    if x1 == x2:
        h = y2 - y1
        if h >= 0:
            lcd_fill(x1, y1, 1, h)
        else:
            lcd_fill(x1, y2, 1, -h)
        return

    # 3) Bresenham-like line for all other slopes
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        # Draw a single pixel using 1-pixel-wide fill
        lcd_fill(x1, y1, 1, 1)

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def lcd_draw_box(x1, y1, x2, y2):
    lcd_draw_h_line(x1, y1, x2)  # top
    lcd_draw_h_line(x1, y2, x2)  # bottom
    lcd_draw_v_line(x1, y1, y2)  # left
    lcd_draw_v_line(x2, y1, y2)  # right


def lcd_start_tone(frequency, volume):
    beeper.freq(frequency)  # Set the frequency
    beeper.duty_u16(volume)  # Set the duty cycle (0 to 1023 for 10-bit resolution)


def lcd_stop_tone():
    beeper.duty_u16(0)  # Turn off the beeper after the duration


FONT_5x7 = {
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    'A': [0x7E, 0x09, 0x09, 0x09, 0x7E],
    'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
    'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
    'D': [0x7F, 0x41, 0x41, 0x22, 0x1C],
    'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
    'F': [0x7F, 0x09, 0x09, 0x09, 0x01],
    'G': [0x3E, 0x41, 0x49, 0x49, 0x7A],
    'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
    'I': [0x00, 0x41, 0x7F, 0x41, 0x00],
    'J': [0x20, 0x40, 0x41, 0x3F, 0x01],
    'K': [0x7F, 0x08, 0x14, 0x22, 0x41],
    'L': [0x7F, 0x40, 0x40, 0x40, 0x40],
    'M': [0x7F, 0x02, 0x04, 0x02, 0x7F],
    'N': [0x7F, 0x04, 0x08, 0x10, 0x7F],
    'O': [0x3E, 0x41, 0x41, 0x41, 0x3E],
    'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
    'Q': [0x3E, 0x41, 0x51, 0x21, 0x5E],
    'R': [0x7F, 0x09, 0x19, 0x29, 0x46],
    'S': [0x46, 0x49, 0x49, 0x49, 0x31],
    'T': [0x01, 0x01, 0x7F, 0x01, 0x01],
    'U': [0x3F, 0x40, 0x40, 0x40, 0x3F],
    'V': [0x1F, 0x20, 0x40, 0x20, 0x1F],
    'W': [0x3F, 0x40, 0x38, 0x40, 0x3F],
    'X': [0x63, 0x14, 0x08, 0x14, 0x63],
    'Y': [0x03, 0x04, 0x78, 0x04, 0x03],
    'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
    '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],
    '1': [0x00, 0x42, 0x7F, 0x40, 0x00],
    '2': [0x62, 0x51, 0x49, 0x49, 0x46],
    '3': [0x22, 0x41, 0x49, 0x49, 0x36],
    '4': [0x18, 0x14, 0x12, 0x7F, 0x10],
    '5': [0x27, 0x45, 0x45, 0x45, 0x39],
    '6': [0x3E, 0x49, 0x49, 0x49, 0x32],
    '7': [0x01, 0x71, 0x09, 0x05, 0x03],
    '8': [0x36, 0x49, 0x49, 0x49, 0x36],
    '9': [0x26, 0x49, 0x49, 0x49, 0x3E],
    '.': [0x00, 0x00, 0x60, 0x60, 0x00],
    ',': [0x00, 0x80, 0x60, 0x20, 0x00],
    '!': [0x00, 0x00, 0x7D, 0x00, 0x00],
    '?': [0x02, 0x01, 0x51, 0x09, 0x06],
    '-': [0x08, 0x08, 0x08, 0x08, 0x08],
    '+': [0x08, 0x08, 0x3E, 0x08, 0x08],
    '/': [0x20, 0x10, 0x08, 0x04, 0x02],
    ':': [0x00, 0x36, 0x36, 0x00, 0x00],
    ';': [0x00, 0x80, 0x76, 0x36, 0x00],
    '\'': [0x00, 0x01, 0x07, 0x00, 0x00],
    '\"': [0x00, 0x03, 0x00, 0x03, 0x00]
}


def lcd_draw_char(x, y, ch, color=(255,255,255)):
    """
    Draw a single 5x7 character at position (x, y) in 'color'.
    """
    # If character not in our FONT_5x7, display a blank or skip
    if ch not in FONT_5x7:
        return
    
    columns = FONT_5x7[ch]  # 5 columns of bitmap data
    lcd_set_color(*color)

    # Each element of 'columns' is a byte, each bit is one pixel
    # top row is LSB (bit 0), bottom row is bit 6 in 5x7 font
    for col_index in range(5):
        col_data = columns[col_index]  # Byte for this column
        for row_index in range(7):
            # Check if the bit is set
            if (col_data >> row_index) & 1:
                # Draw pixel at the correct location
                px = x + col_index
                py = y + row_index
                lcd_draw_pixel(px, py)


def lcd_draw_text(x, y, text, color=(255,255,255)):
    """
    Draw a string at (x, y) with the given color. 
    Each character is 6 pixels wide (5 for the glyph + 1 space).
    """
    cx = x
    for ch in text:
        lcd_draw_char(cx, y, ch, color)
        cx += 6  # Move right by 6 pixels for the next character

def lcd_blit_file(filename, x, y, w, h):
    with open(filename, 'rb') as f:
        data = f.read(w * h * 3)
    lcd_set_range(x, y, w, h)
    lcd_draw()
    spi.write(data)
    