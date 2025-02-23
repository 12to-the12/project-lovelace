# Copyright (c) 2025 by Alfred Morgan <alfred@54.org>
# Copyright (c) 2025 by Mitchell Tucker
# License https://opensource.org/license/isc-license-txt
# ST7796SU1 https://www.displayfuture.com/Display/datasheet/controller/ST7796s.pdf
# Version: 0.0.3

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


def lcd_command(cmd):
    dc.value(0)  # Instruction mode
    spi.write(bytearray([cmd]))


def lcd_data(data):
    dc.value(1)  # Parameter mode
    spi.write(bytearray([data]))


def lcd_reset():
    rst.value(0)
    sleep(0.12)
    rst.value(1)
    sleep(0.12)


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


def lcd_fill(x, y, w, h):
    lcd_set_range(x, y, w, h)
    lcd_draw()
    row = bytearray([r, g, b] * w)
    for _ in range(h):
        spi.write(row)


def lcd_read_data(num_bytes=1):
    dc.value(1)  # Data mode
    response = spi.read(num_bytes)
    return response


def lcd_set_range(x, y, w, h):
    w -= 1
    h -= 1
    lcd_call(0x2A, x >> 8 & 0xFF, x & 0xFF, x + w >> 8 & 0xFF, x + w & 0xFF)
    lcd_call(0x2B, y >> 8 & 0xFF, y & 0xFF, y + h >> 8 & 0xFF, y + h & 0xFF)


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
