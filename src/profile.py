from time import time as epoch
from lcd import *
import time
from time import sleep


def joystick_demo():
    top = 0
    bot = 1e9
    while True:
        # x_floor = 2912
        # x_ceil = 64431
        # x_range = x_ceil - x_floor
        # y_floor = 2992
        # y_ceil = 63951
        # y_range = y_ceil - y_floor
        # x = joy_x.read_u16()
        # y = joy_y.read_u16()

        # x = (x - x_floor) / x_range
        # x -= 0.5
        # x *= 2
        # y = (y - y_floor) / y_range
        # y -= 0.5
        # y *= 2

        x = (joy_x.read_u16() / 2**16 - 0.5) * 2
        y = (joy_y.read_u16() / 2**16 - 0.5) * 2
        print(f"({x:.2f},{y:.2f})")
        sleep(0.1)


# cpu_frequency = 150 * 1e6
# @micropython.native
def profile():
    print("starting...")
    lcd_init()
    while True:
        print("looping")
        r = randint(0, 255)
        g = randint(0, 255)
        start_time = time.ticks_ms()

        lcd_set_color(randint(0, 255), randint(0, 255), randint(0, 255))
        lcd_fill(0, 0, 480, 320)
        # lcd_set_color(randint(0, 255), randint(0, 255), randint(0, 255))
        # for _ in range(10):
        #     lcd_fill(randint(0,400), randint(0,240), 80, 80)
        # for x in range(10):

        #     # lcd_set_color(randint(0, 255), randint(0, 255), randint(0, 255))
        #     # lcd_fill(x, 0, 1, 320)

        #     for y in range(10):
        #         lcd_set_color(randint(0, 255), randint(0, 255), randint(0, 255))
        #         lcd_fill(48 * x, y * 32, 48, 32)

        end_time = time.ticks_ms()

        # cycles = time.ticks_diff(
        #     end_time, start_time
        # )  # How many clock cycles did it take to run the function
        # time_s = cycles / cpu_frequency

        # print(f"time: {time_s:.2f}")
        elapsed_ms = end_time - start_time
        print(f"{elapsed_ms:5.2f}ms")
        print(f"{(320 * 10) / (elapsed_ms / 1_000):5.2f} pixels per second")


# def timefunct(funct):
#     def timed_funct(*args, **kwargs):
#         start = epoch()
#         result = funct(*args, **kwargs)
#         end = epoch()
#         elapsed = end - start
#         elapsed_ms = elapsed * 1e3
#         fps = 60
#         mspf = 1 / 60 * 1e6
#         if elapsed_ms > mspf:
#             print(f"function {funct.__name__} executed in {elapsed_ms:5.2f}ms")
#         return result

#     return timed_funct
