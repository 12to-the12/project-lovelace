from time import time as epoch


class Pulse:
    def __init__(self, period: float = 1) -> None:
        self.period = period
        self.stamp = epoch()

    # def refresh(self):
    #     self.new = epoch()
    #     elapsed = self.new - self.stamp
    #     return elapsed

    def read(self):
        now = epoch()
        if (now - self.stamp) > self.period:
            self.stamp = now
            return True
        else:
            return False
