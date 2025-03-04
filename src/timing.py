from config import config
from time import time

class Pulse:
    def __init__(self, period: float = 1) -> None:
        self.period = period
        self.stamp = time()

    # def refresh(self):
    #     self.new = epoch()
    #     elapsed = self.new - self.stamp
    #     return elapsed

    def read(self):
        now = time()
        if (now - self.stamp) > self.period:
            self.stamp = now
            return True
        else:
            return False


if config.desktop_mode:
    from time import time, sleep

    time_ns = lambda: time() * 1e9
    sleep_us = lambda x: sleep(x / 1e6)
else:
    from time import time_ns, sleep_us

clock_stamp_ns = time_ns()


def clock_wait():
    global clock_stamp_ns
    now = time_ns()
    elapsed_ns = now - clock_stamp_ns

    elapsed = elapsed_ns / 1e9
    target = 1 / config.fps  # seconds per frame
    diff = target - elapsed  # time needed to sleep in seconds
    if elapsed < target:
        # print("sleeping...")
        sleep_us(int(diff * 1e6))

    clock_stamp_ns = time_ns()
